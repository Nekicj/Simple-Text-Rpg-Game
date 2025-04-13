#!/usr/bin/env python3
import os
import random
import json
import time
import sys
import threading
from collections import defaultdict
import pyfiglet
from termcolor import colored
from tqdm import tqdm
from colorama import init, Fore, Back, Style
from pynput import keyboard

init(autoreset=True)

SAVE_FILE = "rpg_save_russian.json"
MAX_LEVEL = 20
XP_THRESHOLD = 100

TITLE_ART = pyfiglet.figlet_format("RPG ИГРА", font="slant")

def animate_text(text, delay=0.03, color='white'):
    for char in text:
        print(colored(char, color), end='', flush=True)
        time.sleep(delay)
    print()

def loading_screen(description="Загрузка", duration=3):
    for _ in tqdm(range(100), desc=colored(description, 'yellow'), 
                 bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"):
        time.sleep(duration/100)
    print()

def frame_text(text, width=60, color='cyan'):
    border = colored('┌' + '─' * (width-2) + '┐', color)
    footer = colored('└' + '─' * (width-2) + '┘', color)
    
    print(border)
    for line in text.split('\n'):
        space = width - 2 - len(line)
        print(colored('│', color) + line + ' ' * space + colored('│', color))
    print(footer)

def sound_effect(effect_type):
    effects = {
        'hit': '\a', 
        'level_up': ''.join(['\a' for _ in range(3)]),
        'error': '\a\a',
        'item': '\a',
        'death': ''.join(['\a' for _ in range(5)])
    }
    if effect_type in effects:
        print(effects[effect_type], end='', flush=True)
        
def animate_battle_effect(attacker, defender, damage, effect_type='hit'):
    animations = {
        'hit': ['   (>o<) ', '  (×_×)  ', ' (>д<)   '],
        'magic': ['  ⋆*･ﾟ  ', ' ★⋆｡˚   ', '☆･⋆。   '],
        'critical': [' ✯✯✯⚔️ ', ' ⚔️⚔️⚔️  ', ' ⚔️✯✯✯  ']
    }
    
    frames = animations.get(effect_type, animations['hit'])
    for frame in frames:
        os.system('cls')
        print(f"\n{colored(attacker, 'green')} атакует {colored(defender, 'red')}!")
        print(colored(frame, 'yellow'))
        print(f"Урон: {colored(str(damage), 'red')}")
        time.sleep(0.2)
    time.sleep(0.3)

CLASS_STATS = {
    "Воин": {"hp": 120, "mp": 20, "strength": 10, "defense": 8, "agility": 5, "critical": 5, "luck": 3},
    "Маг": {"hp": 80, "mp": 100, "strength": 4, "defense": 4, "agility": 7, "critical": 3, "luck": 5},
    "Лучник": {"hp": 90, "mp": 50, "strength": 7, "defense": 5, "agility": 10, "critical": 8, "luck": 7}
}

ENEMIES = [
    {"name": "Гоблин", "hp": 50, "mp": 0, "strength": 5, "defense": 3, "agility": 7, "xp": 20, "gold": 10, 
     "desc": "Мелкий зеленокожий враг с острыми зубами", "attack_msg": "скалит зубы и замахивается дубиной"},
    {"name": "Волк", "hp": 40, "mp": 0, "strength": 6, "defense": 2, "agility": 9, "xp": 15, "gold": 5,
     "desc": "Серый хищник с острыми клыками", "attack_msg": "щелкает челюстями и рычит"},
    {"name": "Орк", "hp": 80, "mp": 10, "strength": 8, "defense": 5, "agility": 4, "xp": 30, "gold": 15,
     "desc": "Массивное зеленое создание с боевым топором", "attack_msg": "издает боевой клич и атакует"},
    {"name": "Скелет", "hp": 60, "mp": 20, "strength": 6, "defense": 4, "agility": 6, "xp": 25, "gold": 12,
     "desc": "Оживлённые кости мертвеца с ржавым мечом", "attack_msg": "лязгает костями и атакует"},
    {"name": "Тролль", "hp": 120, "mp": 5, "strength": 12, "defense": 8, "agility": 2, "xp": 45, "gold": 25,
     "desc": "Огромное и сильное чудовище с дубиной", "attack_msg": "ревет и наносит сокрушительный удар"},
    {"name": "Тёмный маг", "hp": 70, "mp": 80, "strength": 5, "defense": 3, "agility": 7, "xp": 40, "gold": 30,
     "desc": "Колдун в черной мантии с магическим посохом", "attack_msg": "произносит заклинание и атакует темной магией"}
]

ITEMS = {
    "Зелье здоровья": {"type": "consumable", "effect": {"hp": 50}, "value": 20, "description": "Восстанавливает 50 ОЗ"},
    "Зелье маны": {"type": "consumable", "effect": {"mp": 30}, "value": 25, "description": "Восстанавливает 30 ОМ"},
    "Железный меч": {"type": "weapon", "effect": {"strength": 5}, "value": 100, "description": "+5 к Силе"},
    "Стальной меч": {"type": "weapon", "effect": {"strength": 10}, "value": 250, "description": "+10 к Силе"},
    "Кожаная броня": {"type": "armor", "effect": {"defense": 5}, "value": 120, "description": "+5 к Защите"},
    "Стальная броня": {"type": "armor", "effect": {"defense": 10}, "value": 300, "description": "+10 к Защите"},
    "Сапоги быстроты": {"type": "boots", "effect": {"agility": 5}, "value": 150, "description": "+5 к Ловкости"},
    "Магический посох": {"type": "weapon", "effect": {"mp": 20, "strength": 3}, "value": 200, "description": "+3 к Силе, +20 ОМ"},
    "Магическая мантия": {"type": "armor", "effect": {"mp": 15, "defense": 3}, "value": 180, "description": "+3 к Защите, +15 ОМ"},
    "Амулет удачи": {"type": "accessory", "effect": {"luck": 5}, "value": 220, "description": "+5 к Удаче"},
    "Кольцо критического удара": {"type": "accessory", "effect": {"critical": 7}, "value": 280, "description": "+7 к Шансу крит. удара"}
}

QUESTS = [
    {
        "id": "q1",
        "name": "Угроза гоблинов",
        "description": "Победите 3 гоблинов, угрожающих деревне.",
        "objective": {"type": "defeat", "target": "Гоблин", "count": 3},
        "rewards": {"xp": 50, "gold": 30, "items": ["Зелье здоровья"]}
    },
    {
        "id": "q2",
        "name": "Стая волков",
        "description": "Очистите лес от стаи волков.",
        "objective": {"type": "defeat", "target": "Волк", "count": 4},
        "rewards": {"xp": 60, "gold": 25, "items": ["Кожаная броня"]}
    },
    {
        "id": "q3",
        "name": "Тёмная магия",
        "description": "Победите темного мага, который разрушает землю.",
        "objective": {"type": "defeat", "target": "Тёмный маг", "count": 1},
        "rewards": {"xp": 100, "gold": 50, "items": ["Магический посох"]}
    },
    {
        "id": "q4",
        "name": "Древнее зло",
        "description": "Исследуйте древние руины и победите скрытое зло.",
        "objective": {"type": "defeat", "target": "Скелет", "count": 5},
        "rewards": {"xp": 120, "gold": 60, "items": ["Амулет удачи"]}
    },
]

LOCATIONS = [
    {"name": "Деревня", "description": "Мирная деревня с несколькими магазинами.", 
     "enemies": ["Гоблин"], "enemy_chance": 0.2, 
     "ascii_art": r"""
       _   _                              
      | | | |                             
  ____| |_| |__   ___ _ __ _____   ___ __ 
 |_  / __| '_ \ / _ \ '_ \______| | '_ \ 
  / /| |_| | | |  __/ |_) |     | | | | |
 /___|\__|_| |_|\___| .__/      |_|_| |_|
                    | |                   
                    |_|                   
    """},
    {"name": "Лес", "description": "Густой лес с различной живностью.", 
     "enemies": ["Волк", "Гоблин"], "enemy_chance": 0.4, 
     "ascii_art": r"""
      _                       
     | |                      
     | |     ___  ___         
     | |    / _ \/ __|        
     | |___|  __/\__ \        
     \_____/\___||___/        
                              
    """},
    {"name": "Горный перевал", "description": "Опасный горный путь.", 
     "enemies": ["Орк", "Тролль"], "enemy_chance": 0.5, 
     "ascii_art": r"""
    ______  ___  _____ _____ _   _ 
    | ___ \/ _ \|  _  |_   _| \ | |
    | |_/ / /_\ \ | | | | | |  \| |
    |  __/|  _  | | | | | | | . ` |
    | |   | | | \ \_/ / | | | |\  |
    \_|   \_| |_/\___/  \_/ \_| \_/
                                   
    """},
    {"name": "Древние руины", "description": "Остатки древней цивилизации.", 
     "enemies": ["Скелет", "Тёмный маг"], "enemy_chance": 0.6, 
     "ascii_art": r"""
     _____       _____  _   _ _____ 
    |  _  |     |  _  || | | |_   _|
    | | | |_   _| | | || | | | | |  
    | | | | | | | | | || | | | | |  
    \ \_/ / |_| \ \_/ /| |_| | | |  
     \___/ \__, |\___/  \___/  \_/  
            __/ |                   
           |___/                    
    """}
]

class Character:
    def __init__(self, name, char_class):
        self.name = name
        self.char_class = char_class
        self.level = 1
        self.xp = 0
        self.xp_next = XP_THRESHOLD
        self.gold = 50
        
        stats = CLASS_STATS[char_class]
        self.max_hp = stats["hp"]
        self.hp = self.max_hp
        self.max_mp = stats["mp"]
        self.mp = self.max_mp
        self.base_strength = stats["strength"]
        self.base_defense = stats["defense"]
        self.base_agility = stats["agility"]
        self.base_critical = stats["critical"]
        self.base_luck = stats["luck"]
        
        self.equipment = {
            "weapon": None,
            "armor": None,
            "boots": None,
            "accessory": None
        }
        
        self.inventory = defaultdict(int)
        
        if char_class == "Воин":
            self.inventory["Железный меч"] = 1
            self.inventory["Кожаная броня"] = 1
            self.inventory["Зелье здоровья"] = 2
        elif char_class == "Маг":
            self.inventory["Магический посох"] = 1
            self.inventory["Магическая мантия"] = 1
            self.inventory["Зелье маны"] = 2
        elif char_class == "Лучник":
            self.inventory["Железный меч"] = 1
            self.inventory["Сапоги быстроты"] = 1
            self.inventory["Зелье здоровья"] = 2
            
        self.location = "Деревня"
        
        self.active_quests = {}
        self.completed_quests = []
        self.quest_progress = defaultdict(lambda: defaultdict(int))
        
    @property
    def strength(self):
        bonus = 0
        for slot, item_name in self.equipment.items():
            if item_name and "strength" in ITEMS[item_name]["effect"]:
                bonus += ITEMS[item_name]["effect"]["strength"]
        return self.base_strength + bonus
    
    @property
    def defense(self):
        bonus = 0
        for slot, item_name in self.equipment.items():
            if item_name and "defense" in ITEMS[item_name]["effect"]:
                bonus += ITEMS[item_name]["effect"]["defense"]
        return self.base_defense + bonus
    
    @property
    def agility(self):
        bonus = 0
        for slot, item_name in self.equipment.items():
            if item_name and "agility" in ITEMS[item_name]["effect"]:
                bonus += ITEMS[item_name]["effect"]["agility"]
        return self.base_agility + bonus
    
    @property
    def critical(self):
        bonus = 0
        for slot, item_name in self.equipment.items():
            if item_name and "critical" in ITEMS[item_name]["effect"]:
                bonus += ITEMS[item_name]["effect"]["critical"]
        return self.base_critical + bonus
    
    @property
    def luck(self):
        bonus = 0
        for slot, item_name in self.equipment.items():
            if item_name and "luck" in ITEMS[item_name]["effect"]:
                bonus += ITEMS[item_name]["effect"]["luck"]
        return self.base_luck + bonus
    
    def add_xp(self, amount):
        self.xp += amount
        animate_text(f"Вы получили {amount} опыта!", color='yellow')
        
        if self.xp >= self.xp_next and self.level < MAX_LEVEL:
            self.level_up()
    
    def level_up(self):
        sound_effect('level_up')
        self.level += 1
        
        if self.char_class == "Воин":
            self.max_hp += 20
            self.max_mp += 5
            self.base_strength += 3
            self.base_defense += 2
            self.base_agility += 1
            self.base_critical += 1
            self.base_luck += 1
        elif self.char_class == "Маг":
            self.max_hp += 10
            self.max_mp += 20
            self.base_strength += 1
            self.base_defense += 1
            self.base_agility += 2
            self.base_critical += 1
            self.base_luck += 2
        elif self.char_class == "Лучник":
            self.max_hp += 15
            self.max_mp += 10
            self.base_strength += 2
            self.base_defense += 1
            self.base_agility += 3
            self.base_critical += 2
            self.base_luck += 1
        
        self.hp = self.max_hp
        self.mp = self.max_mp
        
        self.xp_next = XP_THRESHOLD * (self.level + 1)
        
        os.system('cls')
        level_art = pyfiglet.figlet_format("УРОВЕНЬ ПОВЫШЕН!", font="slant")
        print(colored(level_art, 'yellow'))
        
        frame_text(f"Вы достигли {self.level} уровня!\n"
                  f"ОЗ: {self.max_hp}\n"
                  f"ОМ: {self.max_mp}\n"
                  f"Сила: {self.base_strength}\n"
                  f"Защита: {self.base_defense}\n"
                  f"Ловкость: {self.base_agility}\n"
                  f"Крит. шанс: {self.base_critical}%\n"
                  f"Удача: {self.base_luck}", width=50, color='cyan')
        
        input("\nНажмите Enter для продолжения...")
    
    def equip_item(self, item_name):
        if item_name not in self.inventory or self.inventory[item_name] <= 0:
            print(colored(f"У вас нет {item_name} в инвентаре.", "red"))
            return False
        
        item = ITEMS[item_name]
        if item["type"] not in ["weapon", "armor", "boots", "accessory"]:
            print(colored(f"Вы не можете экипировать {item_name}. Это {item['type']}.", "red"))
            return False
        
        # Анимация экипировки
        loading_screen("Экипировка предмета", 1)
        
        # Снять текущий предмет
        current_item = self.equipment[item["type"]]
        if current_item:
            self.inventory[current_item] += 1
            print(colored(f"Снято: {current_item}.", "yellow"))
        
        # Экипировать новый предмет
        self.equipment[item["type"]] = item_name
        self.inventory[item_name] -= 1
        
        print(colored(f"Экипировано: {item_name}!", "green"))
        return True
    
    def use_item(self, item_name):
        if item_name not in self.inventory or self.inventory[item_name] <= 0:
            print(colored(f"У вас нет {item_name} в инвентаре.", "red"))
            return False
        
        item = ITEMS[item_name]
        if item["type"] != "consumable":
            print(colored(f"Вы не можете использовать {item_name}. Это {item['type']}.", "red"))
            return False
            
        # Анимация использования
        sound_effect('item')
        
        # Применить эффекты предмета
        for stat, value in item["effect"].items():
            if stat == "hp":
                self.hp = min(self.max_hp, self.hp + value)
                print(colored(f"Восстановлено {value} ОЗ!", "green"))
            elif stat == "mp":
                self.mp = min(self.max_mp, self.mp + value)
                print(colored(f"Восстановлено {value} ОМ!", "blue"))
        
        # Удалить из инвентаря
        self.inventory[item_name] -= 1
        if self.inventory[item_name] <= 0:
            del self.inventory[item_name]
        
        return True
    
    def add_quest(self, quest_id):
        quest = next((q for q in QUESTS if q["id"] == quest_id), None)
        if not quest:
            return False
        
        if quest_id in self.active_quests or quest_id in self.completed_quests:
            print(colored("У вас уже есть это задание или вы его уже выполнили.", "yellow"))
            return False
        
        # Добавить в активные задания
        self.active_quests[quest_id] = quest
        
        # Анимация получения квеста
        os.system('cls')
        quest_art = pyfiglet.figlet_format("НОВЫЙ КВЕСТ", font="small")
        print(colored(quest_art, 'cyan'))
        
        print(colored(f"Новое задание принято: {quest['name']}", "cyan"))
        animate_text(quest['description'], color='white')
        
        objective = quest["objective"]
        print(colored(f"Цель: Победить {objective['count']} {objective['target']}.", "yellow"))
        
        print("\nНаграды:")
        if "xp" in quest["rewards"]:
            print(colored(f"  Опыт: {quest['rewards']['xp']}", "yellow"))
        if "gold" in quest["rewards"]:
            print(colored(f"  Золото: {quest['rewards']['gold']}", "yellow"))
        if "items" in quest["rewards"]:
            for item in quest["rewards"]["items"]:
                print(colored(f"  Предмет: {item}", "green"))
        
        return True
    
    def update_quest_progress(self, enemy_name):
        updated = False
        completed_quests = []
        
        for quest_id, quest in self.active_quests.items():
            objective = quest["objective"]
            if objective["type"] == "defeat" and objective["target"] == enemy_name:
                self.quest_progress[quest_id][enemy_name] += 1
                current = self.quest_progress[quest_id][enemy_name]
                total = objective["count"]
                print(colored(f"Прогресс задания: {quest['name']} - {current}/{total} {enemy_name} побеждено", "cyan"))
                updated = True
                
                # Проверить завершение задания
                if current >= total:
                    completed_quests.append(quest_id)
        
        # Обработать завершенные задания
        for quest_id in completed_quests:
            self.complete_quest(quest_id)
            
        return updated
    
    def complete_quest(self, quest_id):
        if quest_id not in self.active_quests:
            return False
            
        quest = self.active_quests[quest_id]
        rewards = quest["rewards"]
        
        # Анимация завершения задания
        os.system('cls')
        complete_art = pyfiglet.figlet_format("ЗАДАНИЕ ВЫПОЛНЕНО!", font="small")
        print(colored(complete_art, 'green'))
        
        frame_text(f"{quest['name']}\n\n"
                  f"Награды:\n"
                  f"Опыт: {rewards.get('xp', 0)}\n"
                  f"Золото: {rewards.get('gold', 0)}\n"
                  f"Предметы: {', '.join(rewards.get('items', []))}", width=60, color='cyan')
        
        # Выдать награды
        if "xp" in rewards:
            self.add_xp(rewards["xp"])
            
        if "gold" in rewards:
            self.gold += rewards["gold"]
            print(colored(f"Получено {rewards['gold']} золота!", "yellow"))
            
        if "items" in rewards:
            for item in rewards["items"]:
                self.inventory[item] += 1
                print(colored(f"Получен предмет: {item}!", "green"))
                
        # Удалить из активных заданий и добавить в завершенные
        del self.active_quests[quest_id]
        self.completed_quests.append(quest_id)
        
        input("\nНажмите Enter для продолжения...")
        return True
    
    def to_dict(self):
        return {
            "name": self.name,
            "char_class": self.char_class,
            "level": self.level,
            "xp": self.xp,
            "xp_next": self.xp_next,
            "gold": self.gold,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "max_mp": self.max_mp,
            "mp": self.mp,
            "base_strength": self.base_strength,
            "base_defense": self.base_defense,
            "base_agility": self.base_agility,
            "base_critical": self.base_critical,
            "base_luck": self.base_luck,
            "equipment": self.equipment,
            "inventory": dict(self.inventory),
            "location": self.location,
            "active_quests": {k: q["id"] for k, q in self.active_quests.items()},
            "completed_quests": self.completed_quests,
            "quest_progress": {k: dict(v) for k, v in self.quest_progress.items()}
        }
    
    @classmethod
    def from_dict(cls, data):
        character = cls(data["name"], data["char_class"])
        character.level = data["level"]
        character.xp = data["xp"]
        character.xp_next = data["xp_next"]
        character.gold = data["gold"]
        character.max_hp = data["max_hp"]
        character.hp = data["hp"]
        character.max_mp = data["max_mp"]
        character.mp = data["mp"]
        character.base_strength = data["base_strength"]
        character.base_defense = data["base_defense"]
        character.base_agility = data["base_agility"]
        character.base_critical = data["base_critical"]
        character.base_luck = data["base_luck"]
        character.equipment = data["equipment"]
        character.inventory = defaultdict(int, data["inventory"])
        character.location = data["location"]
        
        # Восстановить задания
        character.completed_quests = data["completed_quests"]
        for quest_id in data["active_quests"].values():
            quest = next((q for q in QUESTS if q["id"] == quest_id), None)
            if quest:
                character.active_quests[quest_id] = quest
                
        # Восстановить прогресс заданий
        character.quest_progress = defaultdict(lambda: defaultdict(int))
        for quest_id, progress in data["quest_progress"].items():
            for target, count in progress.items():
                character.quest_progress[quest_id][target] = count
                
        return character


class Combat:
    def __init__(self, character, enemy):
        self.character = character
        self.enemy = self.prepare_enemy(enemy)
        self.turn = 0
        self.effects = []  # Статус эффекты в бою
        
    def prepare_enemy(self, enemy_template):
        """Создать копию шаблона врага"""
        return {**enemy_template}
    
    def character_turn(self, action):
        """Обработать ход персонажа"""
        damage = 0
        effect_type = 'hit'
        
        if action == "attack":
            # Базовая атака
            base_damage = self.character.strength * 2
            dodge_chance = min(0.3, self.enemy["agility"] / 30)
            
            # Влияние удачи на уклонение врага
            dodge_modifier = 1.0 - (self.character.luck / 100)
            dodge_chance *= dodge_modifier
            
            if random.random() < dodge_chance:
                print(colored(f"{self.enemy['name']} уклонился от атаки!", "yellow"))
                return False
                
            # Проверка на критический удар
            crit_chance = min(0.5, self.character.critical / 100)
            crit_hit = False
            
            if random.random() < crit_chance:
                base_damage *= 1.8
                crit_hit = True
                effect_type = 'critical'
                print(colored("КРИТИЧЕСКИЙ УДАР!", "red", attrs=['bold']))
                
            # Рассчитать урон с учетом защиты
            defense_reduction = self.enemy["defense"] / 2
            damage = max(1, base_damage - defense_reduction)
            damage = round(damage * random.uniform(0.8, 1.2))  # Добавить случайность
            
            # Анимация атаки
            if crit_hit:
                animate_battle_effect(self.character.name, self.enemy["name"], damage, 'critical')
            else:
                animate_battle_effect(self.character.name, self.enemy["name"], damage, 'hit')
                
            self.enemy["hp"] -= damage
            print(colored(f"Вы нанесли {self.enemy['name']} {damage} урона!", "green"))
            
        elif action == "special":
            # Специальная атака - стоит ОМ
            if self.character.mp < 10:
                print(colored("Недостаточно ОМ для специальной атаки!", "red"))
                sound_effect('error')
                return False
                
            self.character.mp -= 10
            
            if self.character.char_class == "Воин":
                # Воин: Мощный удар (высокий урон)
                print(colored("Вы используете МОЩНЫЙ УДАР!", "yellow"))
                base_damage = self.character.strength * 3
                defense_reduction = self.enemy["defense"] / 3  # Игнорирует часть защиты
                damage = max(1, base_damage - defense_reduction)
                damage = round(damage * random.uniform(0.9, 1.3))
                effect_type = 'hit'
                
            elif self.character.char_class == "Маг":
                # Маг: Огненный шар (магический урон, игнорирует физическую защиту)
                print(colored("Вы создаете ОГНЕННЫЙ ШАР!", "yellow"))
                base_damage = self.character.strength * 2 + self.character.max_mp / 10
                defense_reduction = self.enemy["defense"] / 4  # В основном игнорирует защиту
                damage = max(1, base_damage - defense_reduction)
                damage = round(damage * random.uniform(0.9, 1.4))
                effect_type = 'magic'
                
                # Шанс наложить эффект горения
                if random.random() < 0.3:
                    self.effects.append({"target": "enemy", "type": "burn", "duration": 3, "power": 5})
                    print(colored(f"{self.enemy['name']} загорелся! (Получает 5 урона каждый ход в течение 3 ходов)", "red"))
                
            elif self.character.char_class == "Лучник":
                # Лучник: Меткий выстрел (шанс критического удара)
                print(colored("Вы делаете МЕТКИЙ ВЫСТРЕЛ!", "yellow"))
                base_damage = self.character.strength * 2.5
                crit_chance = min(0.7, self.character.agility / 20)
                
                if random.random() < crit_chance:
                    print(colored("КРИТИЧЕСКИЙ УДАР!", "red", attrs=['bold']))
                    base_damage *= 1.5
                    effect_type = 'critical'
                    
                defense_reduction = self.enemy["defense"] / 3
                damage = max(1, base_damage - defense_reduction)
                damage = round(damage * random.uniform(0.9, 1.2))
            
            # Анимация атаки
            animate_battle_effect(self.character.name, self.enemy["name"], damage, effect_type)
            
            self.enemy["hp"] -= damage
            print(colored(f"Вы использовали специальную атаку против {self.enemy['name']} и нанесли {damage} урона!", "blue"))
            
        elif action == "use_potion":
            # Пусть игровой цикл обрабатывает использование зелий
            return False
            
        # Обработать эффекты
        self.process_effects()
            
        return True
        
    def enemy_turn(self):
        """Обработать ход врага"""
        # Шанс врага промахнуться
        miss_chance = min(0.2, self.character.agility / 40)
        
        # Влияние удачи на шанс промаха
        miss_modifier = 1.0 + (self.character.luck / 100)
        miss_chance *= miss_modifier
        
        if random.random() < miss_chance:
            print(colored(f"{self.enemy['name']} промахнулся!", "green"))
            return
            
        # Рассчитать урон врага с учетом защиты
        base_damage = self.enemy["strength"] * 1.5
        defense_reduction = self.character.defense / 2
        damage = max(1, base_damage - defense_reduction)
        damage = round(damage * random.uniform(0.8, 1.2))  # Добавить случайность
        
        # Аннимация атаки врага
        print(colored(f"\n{self.enemy['name']} {self.enemy['attack_msg']}!", "yellow"))
        time.sleep(0.5)
        
        # Анимация получения урона
        animate_battle_effect(self.enemy["name"], self.character.name, damage, 'hit')
        
        self.character.hp -= damage
        print(colored(f"{self.enemy['name']} атаковал вас и нанес {damage} урона!", "red"))
        
        # Обработать эффекты после хода врага
        self.process_effects()
        
    def is_character_defeated(self):
        """Проверить, побежден ли персонаж"""
        return self.character.hp <= 0
        
    def is_enemy_defeated(self):
        """Проверить, побежден ли враг"""
        return self.enemy["hp"] <= 0
        
    def process_effects(self):
        """Обработать активные эффекты"""
        if not self.effects:
            return
            
        new_effects = []
        for effect in self.effects:
            effect["duration"] -= 1
            
            if effect["type"] == "burn" and effect["target"] == "enemy":
                burn_damage = effect["power"]
                self.enemy["hp"] -= burn_damage
                print(colored(f"{self.enemy['name']} получает {burn_damage} урона от горения!", "red"))
                
            elif effect["type"] == "poison" and effect["target"] == "character":
                poison_damage = effect["power"]
                self.character.hp -= poison_damage
                print(colored(f"Вы получаете {poison_damage} урона от яда!", "red"))
                
            # Сохранить эффекты с оставшейся длительностью
            if effect["duration"] > 0:
                new_effects.append(effect)
            else:
                print(colored(f"Эффект {effect['type']} закончился!", "yellow"))
                
        self.effects = new_effects
        
    def award_rewards(self):
        """Выдать награды за победу над врагом"""
        if self.is_enemy_defeated():
            victory_art = pyfiglet.figlet_format("ПОБЕДА!", font="banner3-D")
            print(colored(victory_art, 'green'))
            
            animate_text(f"Вы победили {self.enemy['name']}!", color='green')
            
            # Выдать опыт
            xp = self.enemy["xp"]
            print(colored(f"Вы получили {xp} опыта!", "yellow"))
            self.character.add_xp(xp)
            
            # Выдать золото
            gold = self.enemy["gold"]
            print(colored(f"Вы нашли {gold} золота!", "yellow"))
            self.character.gold += gold
            
            # Шанс выпадения предмета (30% + бонус от удачи)
            drop_chance = 0.3 + (self.character.luck / 200)  # Максимум +10% от удачи
            if random.random() < drop_chance:
                # С увеличением уровня могут выпадать лучшие предметы
                if self.character.level >= 3 and random.random() < 0.3:
                    possible_items = ["Зелье здоровья", "Зелье маны", "Амулет удачи"]
                else:
                    possible_items = ["Зелье здоровья", "Зелье маны"]
                    
                item = random.choice(possible_items)
                print(colored(f"{self.enemy['name']} выронил {item}!", "green"))
                self.character.inventory[item] += 1
                
            # Обновить прогресс заданий
            self.character.update_quest_progress(self.enemy["name"])
            
            return True
        return False


class Game:
    def __init__(self):
        self.character = None
        self.running = True
        self.listener = None
        
    def clear_screen(self):
        """Очистить экран терминала"""
        os.system('cls')
        
    def display_title(self):
        """Отобразить заголовок игры"""
        self.clear_screen()
        print(colored(TITLE_ART, 'yellow'))
        print(colored('='*60, 'cyan'))
        print(colored('Добро пожаловать в text rpg, GitHub: @Nekicj '.center(60), 'green'))
        print(colored('='*60, 'cyan'))
        
    def main_menu(self):
        """Отобразить главное меню и обработать опции"""
        while self.running:
            self.display_title()
            
            menu_items = [
                ("Новая игра", "green"),
                ("Загрузить игру", "blue"),
                ("Выход", "red")
            ]
            
            for i, (item, color) in enumerate(menu_items, 1):
                print(colored(f"[{i}] ", 'cyan') + colored(item, color))
            
            choice = input("\nВведите ваш выбор (1-3): ")
            
            if choice == "1":
                self.create_character()
                if self.character:
                    self.game_loop()
            elif choice == "2":
                if self.load_game():
                    self.game_loop()
            elif choice == "3":
                self.running = False
                print(colored("\nСпасибо за игру!", "yellow"))
                break
            else:
                print(colored("Неверный выбор. Попробуйте снова.", "red"))
                input("Нажмите Enter для продолжения...")
                
    def create_character(self):
        """Процесс создания персонажа"""
        self.clear_screen()
        char_art = pyfiglet.figlet_format("СОЗДАНИЕ ГЕРОЯ", font="slant")
        print(colored(char_art, 'green'))
        print(colored('='*60, 'cyan'))
        
        # Получить имя персонажа
        while True:
            name = input(colored("Введите имя персонажа: ", "cyan"))
            if name.strip():
                break
            print(colored("Имя не может быть пустым.", "red"))
            
        # Выбрать класс персонажа
        print(colored("\nВыберите класс:", "cyan"))
        
        classes = [
            ("Воин", "green", "Высокое здоровье и сила, низкая мана"),
            ("Маг", "blue", "Высокая мана, низкое здоровье и защита"),
            ("Лучник", "yellow", "Сбалансированные характеристики с высокой ловкостью")
        ]
        
        for i, (class_name, color, desc) in enumerate(classes, 1):
            print(colored(f"[{i}] ", "cyan") + colored(class_name, color) + f" - {desc}")
        
        while True:
            choice = input(colored("\nВведите ваш выбор (1-3): ", "cyan"))
            if choice == "1":
                char_class = "Воин"
                break
            elif choice == "2":
                char_class = "Маг"
                break
            elif choice == "3":
                char_class = "Лучник"
                break
            else:
                print(colored("Неверный выбор. Попробуйте снова.", "red"))
        
        # Эффект создания персонажа
        print(colored("\nСоздание персонажа...", "yellow"))
        loading_screen("Создание персонажа", 2)
                
        # Создать персонажа
        self.character = Character(name, char_class)
        
        # Отобразить информацию о персонаже
        self.display_character_info()
        
        print(colored("\nПерсонаж успешно создан!", "green"))
        
        # Добавить стартовый квест
        self.character.add_quest("q1")
        
        input("\nНажмите Enter, чтобы начать приключение...")
        return True
        
    def display_character_info(self):
        """Отображает статистику и экипировку персонажа"""
        if not self.character:
            return
            
        char = self.character
        
        self.clear_screen()
        char_art = pyfiglet.figlet_format(f"{char.name}", font="small")
        print(colored(char_art, 'cyan'))
        
        frame_text(f"Класс: {char.char_class} | Уровень: {char.level} | Локация: {char.location}\n"
                  f"Золото: {char.gold} | Опыт: {char.xp}/{char.xp_next}", width=60, color='yellow')
        
        # Характеристики
        print(colored("\n◉ ХАРАКТЕРИСТИКИ:", "cyan"))
        print(colored(f"ОЗ: {char.hp}/{char.max_hp}", "green"))
        print(colored(f"ОМ: {char.mp}/{char.max_mp}", "blue"))
        print(colored(f"Сила: {char.strength} ({char.base_strength} + {char.strength - char.base_strength})", "red"))
        print(colored(f"Защита: {char.defense} ({char.base_defense} + {char.defense - char.base_defense})", "magenta"))
        print(colored(f"Ловкость: {char.agility} ({char.base_agility} + {char.agility - char.base_agility})", "yellow"))
        print(colored(f"Крит. шанс: {char.critical}% ({char.base_critical}% + {char.critical - char.base_critical}%)", "red"))
        print(colored(f"Удача: {char.luck} ({char.base_luck} + {char.luck - char.base_luck})", "green"))
        
        # Экипировка
        print(colored("\n◉ ЭКИПИРОВКА:", "cyan"))
        for slot, item in char.equipment.items():
            slot_names = {"weapon": "Оружие", "armor": "Броня", "boots": "Обувь", "accessory": "Аксессуар"}
            if item:
                item_desc = ITEMS[item]["description"]
                print(f"{colored(slot_names[slot], 'white')}: {colored(item, 'green')} {colored(f'({item_desc})', 'yellow')}")
            else:
                print(f"{colored(slot_names[slot], 'white')}: {colored('Пусто', 'red')}")
                
        # Активные задания
        if char.active_quests:
            print(colored("\n◉ АКТИВНЫЕ ЗАДАНИЯ:", "cyan"))
            for quest_id, quest in char.active_quests.items():
                objective = quest["objective"]
                current = char.quest_progress[quest_id].get(objective["target"], 0)
                total = objective["count"]
                print(f"{colored(quest['name'], 'white')}: {colored(f'{current}/{total} {objective["target"]} побеждено', 'yellow')}")
                
    def display_inventory(self):
        """Отображает инвентарь персонажа с возможностью использовать или экипировать предметы"""
        if not self.character:
            return
            
        while True:
            self.clear_screen()
            inv_art = pyfiglet.figlet_format("ИНВЕНТАРЬ", font="small")
            print(colored(inv_art, 'yellow'))
            
            print(colored(f"Золото: {self.character.gold}", "yellow"))
            
            if not self.character.inventory:
                print(colored("\nВаш инвентарь пуст.", "red"))
                input("\nНажмите Enter для возврата...")
                return
                
            # Отобразить предметы с нумерацией для выбора
            print(colored("\n◉ ПРЕДМЕТЫ:", "cyan"))
            items = list(self.character.inventory.items())
            
            # Сгруппировать предметы по типу
            grouped_items = {"consumable": [], "weapon": [], "armor": [], "boots": [], "accessory": []}
            for item_name, count in items:
                item = ITEMS[item_name]
                grouped_items[item["type"]].append((item_name, count))
                
            # Отобразить по группам
            type_names = {
                "consumable": "Расходные предметы",
                "weapon": "Оружие",
                "armor": "Броня",
                "boots": "Обувь",
                "accessory": "Аксессуары"
            }
            
            item_counter = 1
            for item_type, type_items in grouped_items.items():
                if type_items:
                    print(colored(f"\n{type_names[item_type]}:", "yellow"))
                    for item_name, count in type_items:
                        item = ITEMS[item_name]
                        equipped = ""
                        if item_type != "consumable" and item_name in self.character.equipment.values():
                            equipped = colored(" [НАДЕТО]", "green")
                            
                        print(colored(f"[{item_counter}] ", "cyan") + colored(f"{item_name} (x{count}){equipped}", "white") + 
                              f" - {colored(item['description'], 'yellow')}")
                        item_counter += 1
                    
            print("\n" + colored("[И] ", "cyan") + colored("Использовать/Экипировать предмет", "green"))
            print(colored("[Н] ", "cyan") + colored("Назад", "red"))
            
            choice = input("\nВаш выбор: ").lower()
            
            if choice == 'н':
                break
            elif choice == 'и':
                # Выбрать предмет для использования или экипировки
                try:
                    flat_items = [item for sublist in grouped_items.values() for item in sublist]
                    item_num = int(input(f"\nВведите номер предмета (1-{len(flat_items)}): "))
                    
                    if 1 <= item_num <= len(flat_items):
                        item_name = flat_items[item_num-1][0]
                        item = ITEMS[item_name]
                        
                        if item["type"] == "consumable":
                            self.character.use_item(item_name)
                        else:
                            self.character.equip_item(item_name)
                            
                        input("\nНажмите Enter для продолжения...")
                    else:
                        print(colored("Неверный номер предмета.", "red"))
                        input("\nНажмите Enter для продолжения...")
                except ValueError:
                    print(colored("Пожалуйста, введите корректное число.", "red"))
                    input("\nНажмите Enter для продолжения...")
            else:
                print(colored("Неверный выбор.", "red"))
                input("\nНажмите Enter для продолжения...")
                
    def shop_menu(self):
        """Отображает магазин с товарами для покупки"""
        if not self.character:
            return
            
        # Магазин только в Деревне
        if self.character.location != "Деревня":
            print(colored("В этой локации нет магазина. Необходимо быть в Деревне.", "red"))
            input("\nНажмите Enter для продолжения...")
            return
            
        while True:
            self.clear_screen()
            shop_art = pyfiglet.figlet_format("МАГАЗИН", font="small")
            print(colored(shop_art, 'cyan'))
            
            frame_text(f"Ваше золото: {self.character.gold}", width=40, color='yellow')
            
            # Отобразить товары для продажи с нумерацией
            print(colored("\n◉ ТОВАРЫ:", "cyan"))
            shop_items = [
                "Зелье здоровья", "Зелье маны", "Железный меч", "Кожаная броня", 
                "Сапоги быстроты", "Стальной меч", "Стальная броня", "Магический посох", 
                "Магическая мантия", "Амулет удачи", "Кольцо критического удара"
            ]
            
            # Сгруппировать товары по типу
            grouped_items = {"consumable": [], "weapon": [], "armor": [], "boots": [], "accessory": []}
            for item_name in shop_items:
                item = ITEMS[item_name]
                grouped_items[item["type"]].append(item_name)
                
            # Отобразить по группам
            type_names = {
                "consumable": "Зелья и расходники",
                "weapon": "Оружие",
                "armor": "Броня",
                "boots": "Обувь",
                "accessory": "Аксессуары"
            }
            
            item_counter = 1
            for item_type, type_items in grouped_items.items():
                if type_items:
                    print(colored(f"\n{type_names[item_type]}:", "yellow"))
                    for item_name in type_items:
                        item = ITEMS[item_name]
                        price = item["value"]
                        color = "white"
                        if self.character.gold < price:
                            color = "red"  # Недостаточно золота
                            
                        print(colored(f"[{item_counter}] ", "cyan") + 
                              colored(f"{item_name.ljust(20)}", color) + 
                              colored(f"{price} золота", "yellow") + 
                              f" - {item['description']}")
                        item_counter += 1
                    
            print("\n" + colored("[К] ", "cyan") + colored("Купить предмет", "green"))
            print(colored("[П] ", "cyan") + colored("Продать предмет", "green"))
            print(colored("[Н] ", "cyan") + colored("Назад", "red"))
            
            choice = input("\nВаш выбор: ").lower()
            
            if choice == 'н':
                break
            elif choice == 'к':
                # Купить предмет
                flat_items = [item for sublist in grouped_items.values() for item in sublist]
                
                try:
                    item_num = int(input(f"\nВведите номер предмета для покупки (1-{len(flat_items)}): "))
                    if 1 <= item_num <= len(flat_items):
                        item_name = flat_items[item_num-1]
                        item = ITEMS[item_name]
                        price = item["value"]
                        
                        if self.character.gold >= price:
                            # Эффект покупки
                            loading_screen("Покупка предмета", 1)
                            
                            self.character.gold -= price
                            self.character.inventory[item_name] += 1
                            print(colored(f"Вы купили {item_name} за {price} золота.", "green"))
                            sound_effect('item')
                        else:
                            print(colored(f"Недостаточно золота для покупки {item_name}.", "red"))
                            sound_effect('error')
                            
                        input("\nНажмите Enter для продолжения...")
                    else:
                        print(colored("Неверный номер предмета.", "red"))
                        input("\nНажмите Enter для продолжения...")
                except ValueError:
                    print(colored("Пожалуйста, введите корректное число.", "red"))
                    input("\nНажмите Enter для продолжения...")
            
            elif choice == 'п':
                # Продать предмет
                if not self.character.inventory:
                    print(colored("У вас нет предметов для продажи.", "red"))
                    input("\nНажмите Enter для продолжения...")
                    continue
                    
                # Отобразить инвентарь для продажи (полцены)
                self.clear_screen()
                print(colored("ПРОДАЖА ПРЕДМЕТОВ", "yellow"))
                print(colored(f"Ваше золото: {self.character.gold}", "yellow"))
                
                print(colored("\nВаши предметы:", "cyan"))
                items = list(self.character.inventory.items())
                for i, (item_name, count) in enumerate(items, 1):
                    item = ITEMS[item_name]
                    sell_price = item["value"] // 2
                    
                    # Нельзя продать экипированные предметы
                    if item_name in self.character.equipment.values():
                        print(colored(f"[{i}] ", "cyan") + 
                              colored(f"{item_name} (x{count}) - [НАДЕТО]", "red"))
                        continue
                        
                    print(colored(f"[{i}] ", "cyan") + 
                          colored(f"{item_name} (x{count})", "white") + 
                          colored(f" - Продать за {sell_price} золота", "yellow"))
                    
                try:
                    item_num = int(input(f"\nВведите номер предмета для продажи (1-{len(items)}) или 0 для отмены: "))
                    if item_num == 0:
                        continue
                        
                    if 1 <= item_num <= len(items):
                        item_name = items[item_num-1][0]
                        item = ITEMS[item_name]
                        sell_price = item["value"] // 2
                        
                        # Проверка на экипировку
                        if item_name in self.character.equipment.values():
                            print(colored("Нельзя продать экипированный предмет. Сначала снимите его.", "red"))
                            input("\nНажмите Enter для продолжения...")
                            continue
                        
                        # Подтвердить продажу
                        confirm = input(f"Продать {item_name} за {sell_price} золота? (д/н): ").lower()
                        if confirm == 'д':
                            # Эффект продажи
                            loading_screen("Продажа предмета", 1)
                            
                            self.character.inventory[item_name] -= 1
                            if self.character.inventory[item_name] <= 0:
                                del self.character.inventory[item_name]
                                
                            self.character.gold += sell_price
                            print(colored(f"Вы продали {item_name} за {sell_price} золота.", "green"))
                            sound_effect('item')
                        
                        input("\nНажмите Enter для продолжения...")
                    else:
                        print(colored("Неверный номер предмета.", "red"))
                        input("\nНажмите Enter для продолжения...")
                except ValueError:
                    print(colored("Пожалуйста, введите корректное число.", "red"))
                    input("\nНажмите Enter для продолжения...")
            else:
                print(colored("Неверный выбор.", "red"))
                input("\nНажмите Enter для продолжения...")
    
    def travel_menu(self):
        """Отображает доступные локации для путешествия"""
        if not self.character:
            return
            
        self.clear_screen()
        travel_art = pyfiglet.figlet_format("ПУТЕШЕСТВИЕ", font="small")
        print(colored(travel_art, 'yellow'))
        
        # Текущая локация
        location = next((loc for loc in LOCATIONS if loc["name"] == self.character.location), LOCATIONS[0])
        
        # Отобразить ASCII-арт текущей локации
        print(colored(location["ascii_art"], "cyan"))
        
        frame_text(f"Текущая локация: {location['name']}\n{location['description']}", 
                  width=60, color='green')
        
        # Отобразить доступные локации
        print(colored("\n◉ ДОСТУПНЫЕ НАПРАВЛЕНИЯ:", "cyan"))
        
        for i, loc in enumerate(LOCATIONS, 1):
            if loc["name"] != self.character.location:
                danger_level = ""
                if loc["enemy_chance"] < 0.3:
                    danger_level = colored("■□□ (Низкая опасность)", "green")
                elif loc["enemy_chance"] < 0.5:
                    danger_level = colored("■■□ (Средняя опасность)", "yellow")
                else:
                    danger_level = colored("■■■ (Высокая опасность)", "red")
                    
                print(colored(f"[{i}] ", "cyan") + 
                      colored(f"{loc['name']}", "white") + 
                      f" - {loc['description']} {danger_level}")
                
        print("\n" + colored("[Н] ", "cyan") + colored("Назад", "red"))
        
        choice = input("\nВаш выбор: ").lower()
        
        if choice == 'н':
            return
            
        try:
            choice = int(choice)
            if 1 <= choice <= len(LOCATIONS):
                new_location = LOCATIONS[choice-1]
                if new_location["name"] != self.character.location:
                    # Эффект путешествия
                    self.clear_screen()
                    print(colored(f"Путешествие в {new_location['name']}...", "yellow"))
                    loading_screen("В пути", 2)
                    
                    # Шанс случайного боя при путешествии
                    if random.random() < 0.4:  # 40% шанс встретить врага
                        print(colored("\nВо время путешествия вы столкнулись с врагом!", "red"))
                        input("\nНажмите Enter для продолжения...")
                        self.handle_combat()
                        
                    # Сменить локацию если выжил в бою
                    if not self.character.hp <= 0:
                        self.character.location = new_location["name"]
                        
                        # Отобразить новую локацию
                        self.clear_screen()
                        print(colored(new_location["ascii_art"], "cyan"))
                        
                        print(colored(f"\nВы прибыли в {new_location['name']}!", "green"))
                        animate_text(new_location["description"], color='white')
                    
            else:
                print(colored("Неверное направление.", "red"))
        except ValueError:
            print(colored("Пожалуйста, введите корректное число.", "red"))
            
        input("\nНажмите Enter для продолжения...")
    
    def handle_combat(self):
        """Обработать боевое столкновение"""
        if not self.character:
            return
            
        # Получить врагов для текущей локации
        location = next((loc for loc in LOCATIONS if loc["name"] == self.character.location), LOCATIONS[0])
        possible_enemies = location["enemies"]
        
        # Выбрать случайного врага
        enemy_name = random.choice(possible_enemies)
        enemy_template = next((e for e in ENEMIES if e["name"] == enemy_name), ENEMIES[0])
        
        # Масштабировать врага с учетом уровня персонажа
        level_scale = 1 + (self.character.level - 1) * 0.2
        enemy_template = enemy_template.copy()
        enemy_template["hp"] = int(enemy_template["hp"] * level_scale)
        enemy_template["strength"] = int(enemy_template["strength"] * level_scale)
        enemy_template["defense"] = int(enemy_template["defense"] * level_scale)
        
        # Начать бой с эффектом
        self.clear_screen()
        battle_art = pyfiglet.figlet_format("БОЙ!", font="banner3-D")
        print(colored(battle_art, 'red'))
        
        print(colored(f"Вы столкнулись с {enemy_name}!", "red"))
        print(colored(f"Описание: {enemy_template['desc']}", "yellow"))
        
        loading_screen("Подготовка к бою", 1)
        
        # Создать экземпляр боя
        combat = Combat(self.character, enemy_template)
        
        # Цикл боя
        while not combat.is_character_defeated() and not combat.is_enemy_defeated():
            self.clear_screen()
            enemy = combat.enemy
            
            # Отобразить UI боя
            print(colored("╔" + "═" * 58 + "╗", "red"))
            print(colored("║", "red") + colored(" БОЙ! ".center(58), "yellow") + colored("║", "red"))
            print(colored("╚" + "═" * 58 + "╝", "red"))
            
            # Характеристики персонажа
            hp_percent = self.character.hp / self.character.max_hp
            hp_bar = "■" * int(hp_percent * 20) + "□" * (20 - int(hp_percent * 20))
            
            mp_percent = self.character.mp / self.character.max_mp
            mp_bar = "■" * int(mp_percent * 20) + "□" * (20 - int(mp_percent * 20))
            
            hp_color = "green"
            if hp_percent < 0.3:
                hp_color = "red"
            elif hp_percent < 0.7:
                hp_color = "yellow"
            
            mp_color = "blue"
            if mp_percent < 0.3:
                mp_color = "red"
            elif mp_percent < 0.5:
                mp_color = "magenta"
            
            print(f"\n{colored('Вы', 'green')}: {self.character.name} | {colored('Уровень', 'cyan')} {self.character.level} {self.character.char_class}")
            print(f"{colored('ОЗ', hp_color)}: {self.character.hp}/{self.character.max_hp} {colored(hp_bar, hp_color)}")
            print(f"{colored('ОМ', mp_color)}: {self.character.mp}/{self.character.max_mp} {colored(mp_bar, mp_color)}")
            
            # Характеристики врага
            enemy_hp_percent = enemy["hp"] / enemy_template["hp"]
            enemy_hp_bar = "■" * int(enemy_hp_percent * 20) + "□" * (20 - int(enemy_hp_percent * 20))
            enemy_hp_color = "green"
            if enemy_hp_percent < 0.3:
                enemy_hp_color = "red"
            elif enemy_hp_percent < 0.7:
                enemy_hp_color = "yellow"
                
            print(f"\n{colored(enemy['name'], 'red')} | {colored('ОЗ', enemy_hp_color)}: {enemy['hp']} {colored(enemy_hp_bar, enemy_hp_color)}")
            
            # Варианты боя
            print(colored("\n▶ Действия:", "cyan"))
            print(colored("[1] ", "cyan") + colored("Атака", "white") + " - Базовая атака")
            print(colored("[2] ", "cyan") + colored("Специальная атака", "blue") + f" (10 ОМ) - Особая атака класса {self.character.char_class}")
            print(colored("[3] ", "cyan") + colored("Использовать зелье", "green") + " - Восстановить ОЗ/ОМ")
            print(colored("[4] ", "cyan") + colored("Бежать", "yellow") + " - Попытаться сбежать (50% шанс)")
            
            choice = input("\nВыберите действие: ")
            
            if choice == "1":
                # Базовая атака
                if combat.character_turn("attack"):
                    # Ход врага если атака была успешной
                    if not combat.is_enemy_defeated():
                        combat.enemy_turn()
                else:
                    input("\nНажмите Enter для продолжения...")
                    
            elif choice == "2":
                # Специальная атака
                if combat.character_turn("special"):
                    # Ход врага если атака была успешной
                    if not combat.is_enemy_defeated():
                        combat.enemy_turn()
                else:
                    input("\nНажмите Enter для продолжения...")
                    
            elif choice == "3":
                # Показать доступные зелья
                potions = [(item, count) for item, count in self.character.inventory.items() 
                          if ITEMS[item]["type"] == "consumable" and count > 0]
                
                if not potions:
                    print(colored("У вас нет зелий!", "red"))
                    sound_effect('error')
                    input("\nНажмите Enter для продолжения...")
                    continue
                    
                print(colored("\nДоступные зелья:", "cyan"))
                for i, (potion, count) in enumerate(potions, 1):
                    print(colored(f"[{i}] ", "cyan") + 
                          colored(f"{potion} (x{count})", "white") + 
                          f" - {ITEMS[potion]['description']}")
                    
                try:
                    potion_choice = int(input("\nВыберите зелье (0 для отмены): "))
                    if potion_choice == 0:
                        continue
                        
                    if 1 <= potion_choice <= len(potions):
                        potion_name = potions[potion_choice-1][0]
                        if self.character.use_item(potion_name):
                            # Ход врага после использования зелья
                            combat.enemy_turn()
                except ValueError:
                    print(colored("Неверный выбор.", "red"))
                    input("\nНажмите Enter для продолжения...")
                    
            elif choice == "4":
                # Попытаться сбежать (50% шанс)
                print(colored("\nВы пытаетесь сбежать...", "yellow"))
                time.sleep(1)
                
                if random.random() < 0.5:
                    print(colored("Вы успешно сбежали!", "green"))
                    input("\nНажмите Enter для продолжения...")
                    return
                else:
                    print(colored("Вам не удалось сбежать!", "red"))
                    # Враг получает бесплатную атаку
                    combat.enemy_turn()
                    
            else:
                print(colored("Неверный выбор.", "red"))
                
            # Пауза чтобы игрок мог прочитать сообщения боя
            if not combat.is_character_defeated() and not combat.is_enemy_defeated():
                input("\nНажмите Enter для продолжения...")
                
        # Бой завершен
        if combat.is_enemy_defeated():
            combat.award_rewards()
            input("\nНажмите Enter для продолжения...")
        elif combat.is_character_defeated():
            self.clear_screen()
            defeat_art = pyfiglet.figlet_format("ПОРАЖЕНИЕ", font="banner3-D")
            print(colored(defeat_art, 'red'))
            sound_effect('death')
            
            # Позволить игроку продолжить с низким здоровьем
            self.character.hp = 1
            print(colored("\nБоги улыбнулись вам и сохранили вашу жизнь.", "green"))
            print(colored("Вы просыпаетесь с 1 ОЗ обратно в Деревне.", "green"))
            self.character.location = "Деревня"
            input("\nНажмите Enter для продолжения...")
    
    def quest_menu(self):
        """Отображает активные задания и доступные задания"""
        if not self.character:
            return
            
        self.clear_screen()
        quest_art = pyfiglet.figlet_format("ЗАДАНИЯ", font="small")
        print(colored(quest_art, 'cyan'))
        
        # Отобразить активные задания
        if self.character.active_quests:
            print(colored("\n◉ АКТИВНЫЕ ЗАДАНИЯ:", "cyan"))
            for quest_id, quest in self.character.active_quests.items():
                objective = quest["objective"]
                current = self.character.quest_progress[quest_id].get(objective["target"], 0)
                total = objective["count"]
                
                progress_bar = "■" * current + "□" * (total - current)
                
                print(colored(f"{quest['name']}", "yellow"))
                print(f"  {colored(quest['description'], 'white')}")
                print(f"  Прогресс: {colored(f'{current}/{total} {objective['target']} побеждено', 'green')} {progress_bar}")
                
                # Отобразить награды
                rewards = quest["rewards"]
                print(f"  Награды: {colored(f'Опыт: {rewards.get('xp', 0)}', 'yellow')} | " + 
                      f"{colored(f'Золото: {rewards.get('gold', 0)}', 'yellow')} | " + 
                      f"{colored(f'Предметы: {', '.join(rewards.get('items', []))}', 'green')}")
                print()
        else:
            print(colored("\nУ вас нет активных заданий.", "yellow"))
            
        # Отобразить доступные задания (если в Деревне)
        if self.character.location == "Деревня":
            available_quests = [q for q in QUESTS if q["id"] not in self.character.active_quests 
                                and q["id"] not in self.character.completed_quests]
            
            if available_quests:
                print(colored("\n◉ ДОСТУПНЫЕ ЗАДАНИЯ:", "cyan"))
                for i, quest in enumerate(available_quests, 1):
                    print(colored(f"[{i}] ", "cyan") + 
                          colored(f"{quest['name']}", "yellow") + 
                          f": {quest['description']}")
                    
                print("\n" + colored("[П] ", "cyan") + colored("Принять задание", "green"))
                
                choice = input("\nВведите ваш выбор (или любую другую клавишу для возврата): ").lower()
                
                if choice == 'п':
                    try:
                        quest_num = int(input(f"Введите номер задания (1-{len(available_quests)}): "))
                        if 1 <= quest_num <= len(available_quests):
                            quest = available_quests[quest_num-1]
                            self.character.add_quest(quest["id"])
                        else:
                            print(colored("Неверный номер задания.", "red"))
                            input("\nНажмите Enter для продолжения...")
                    except ValueError:
                        print(colored("Пожалуйста, введите корректное число.", "red"))
                        input("\nНажмите Enter для продолжения...")
            else:
                print(colored("\nНет новых заданий в этой локации.", "yellow"))
        else:
            print(colored("\nПосетите Деревню, чтобы принять новые задания.", "yellow"))
            
        # Отобразить завершенные задания
        if self.character.completed_quests:
            print(colored("\n◉ ЗАВЕРШЕННЫЕ ЗАДАНИЯ:", "green"))
            for quest_id in self.character.completed_quests:
                quest = next((q for q in QUESTS if q["id"] == quest_id), None)
                if quest:
                    print(colored(f"✓ {quest['name']}", "green"))
                    
        input("\nНажмите Enter для продолжения...")
    
    def explore(self):
        """Исследовать текущую локацию для случайных встреч"""
        if not self.character:
            return
            
        # Получить данные текущей локации
        location = next((loc for loc in LOCATIONS if loc["name"] == self.character.location), LOCATIONS[0])
        
        self.clear_screen()
        print(colored(f"ИССЛЕДОВАНИЕ {location['name']}".center(60), "yellow"))
        print(colored("="*60, "cyan"))
        
        print(colored(location["ascii_art"], "cyan"))
        animate_text(f"Вы исследуете {location['name']}...", color='white')
        
        # Эффект исследования
        loading_screen("Исследование местности", 2)
        
        # Случайный шанс встречи с врагом в зависимости от локации
        if random.random() < location["enemy_chance"]:
            print(colored("\nВы столкнулись с врагом!", "red"))
            sound_effect('hit')
            input("\nНажмите Enter для продолжения...")
            self.handle_combat()
        else:
            # Нет врага, но может быть найдется что-то
            if random.random() < 0.4:  # 40% шанс найти что-то
                item_chance = random.random()
                
                if item_chance < 0.7:  # 70% времени найти зелье
                    if random.random() < 0.5:
                        item = "Зелье здоровья"
                    else:
                        item = "Зелье маны"
                        
                    self.character.inventory[item] += 1
                    print(colored(f"\nВы нашли {item}!", "green"))
                    sound_effect('item')
                else:  # 30% времени найти золото
                    gold = random.randint(5, 20)
                    self.character.gold += gold
                    print(colored(f"\nВы нашли {gold} золота!", "yellow"))
            else:
                print(colored("\nВы исследовали местность, но не нашли ничего интересного.", "white"))
                
        input("\nНажмите Enter для продолжения...")
    
    def rest(self):
        """Отдых для восстановления ОЗ и ОМ (только в Деревне)"""
        if not self.character:
            return
            
        if self.character.location != "Деревня":
            print(colored("Вы можете отдыхать только в Деревне.", "red"))
            input("\nНажмите Enter для продолжения...")
            return
        rest_cost = 10
        
        self.clear_screen()
        rest_art = pyfiglet.figlet_format("ТАВЕРНА", font="small")
        print(colored(rest_art, 'yellow'))
        
        frame_text(f"Таверна \"Сонный Тролль\"\nСтоимость ночлега: {rest_cost} золота", width=50, color='yellow')
        
        print(colored(f"\nВаше золото: {self.character.gold}", "yellow"))
        print(colored(f"Текущее здоровье: {self.character.hp}/{self.character.max_hp}", "green"))
        print(colored(f"Текущая мана: {self.character.mp}/{self.character.max_mp}", "blue"))
        
        if self.character.gold < rest_cost:
            print(colored("\nУ вас недостаточно золота для отдыха.", "red"))
            input("\nНажмите Enter для продолжения...")
            return
            
        choice = input(colored(f"\nОтдохнуть за {rest_cost} золота? (д/н): ", "cyan")).lower()
        
        if choice == 'д':
            self.character.gold -= rest_cost
            
            # Анимация отдыха
            print(colored("\nВы отдыхаете в таверне...", "yellow"))
            loading_screen("Сон", 2)
            
            self.character.hp = self.character.max_hp
            self.character.mp = self.character.max_mp
            
            print(colored("\nВы хорошо отдохнули и чувствуете себя полностью восстановленным!", "green"))
            print(colored("ОЗ и ОМ полностью восстановлены!", "green"))
        
        input("\nНажмите Enter для продолжения...")
    
    def save_game(self):
        """Сохранить игру в файл"""
        if not self.character:
            print(colored("Нет персонажа для сохранения.", "red"))
            return False
            
        try:
            # Конвертировать персонажа в словарь
            save_data = self.character.to_dict()
            
            # Анимация сохранения
            print(colored("\nСохранение игры...", "yellow"))
            loading_screen("Сохранение данных", 1)
            
            # Сохранить в файл
            with open(SAVE_FILE, 'w') as f:
                json.dump(save_data, f, indent=2)
                
            print(colored("\nИгра успешно сохранена!", "green"))
            return True
            
        except Exception as e:
            print(colored(f"\nОшибка при сохранении игры: {str(e)}", "red"))
            return False
            
    def load_game(self):
        """Загрузить игру из файла"""
        try:
            if not os.path.exists(SAVE_FILE):
                print(colored("\nФайл сохранения не найден.", "red"))
                input("\nНажмите Enter для продолжения...")
                return False
                
            # Анимация загрузки
            print(colored("\nЗагрузка сохраненной игры...", "yellow"))
            loading_screen("Загрузка данных", 1)
            
            # Загрузить из файла
            with open(SAVE_FILE, 'r') as f:
                save_data = json.load(f)
                
            self.character = Character.from_dict(save_data)
            
            print(colored("\nИгра успешно загружена!", "green"))
            input("\nНажмите Enter для продолжения...")
            return True
            
        except Exception as e:
            print(colored(f"\nОшибка при загрузке игры: {str(e)}", "red"))
            input("\nНажмите Enter для продолжения...")
            return False
    
    def game_loop(self):
        """Основной игровой цикл"""
        if not self.character:
            return
            
        while self.running and self.character:
            # Проверка на случайное событие
            location = next((loc for loc in LOCATIONS if loc["name"] == self.character.location), LOCATIONS[0])
            if random.random() < location["enemy_chance"] * 0.3:  # Уменьшенный шанс по сравнению с исследованием
                print(colored(f"\nВы столкнулись с врагом в локации {self.character.location}!", "red"))
                sound_effect('hit')
                input("\nНажмите Enter для продолжения...")
                self.handle_combat()
                
                if self.character.hp <= 0:
                    continue
                    
            # Отобразить главное игровое меню
            self.clear_screen()
            title_art = pyfiglet.figlet_format(f"{self.character.name}", font="small")
            print(colored(title_art, 'cyan'))
            
            # Текущая локация
            location = next((loc for loc in LOCATIONS if loc["name"] == self.character.location), LOCATIONS[0])
            print(colored(location["ascii_art"], "cyan"))
            
            # Информация о персонаже
            char = self.character
            
            hp_percent = self.character.hp / self.character.max_hp
            hp_bar = "■" * int(hp_percent * 20) + "□" * (20 - int(hp_percent * 20))
            hp_color = "green"
            if hp_percent < 0.3:
                hp_color = "red"
            elif hp_percent < 0.7:
                hp_color = "yellow"
                
            print(colored(f"Локация: {char.location}", "green"))
            print(f"{colored('Уровень:', 'yellow')} {char.level} | {colored('Класс:', 'yellow')} {char.char_class} | {colored('Золото:', 'yellow')} {char.gold}")
            print(f"{colored('ОЗ:', hp_color)} {char.hp}/{char.max_hp} {colored(hp_bar, hp_color)}")
            print(f"{colored('Опыт:', 'blue')} {char.xp}/{char.xp_next}")
            
            # Кнопки активных заданий
            if char.active_quests:
                print(colored("\n▶ АКТИВНЫЕ ЗАДАНИЯ:", "yellow"))
                for quest_id, quest in list(char.active_quests.items())[:2]:  # Показать только 2 активных задания
                    objective = quest["objective"]
                    current = char.quest_progress[quest_id].get(objective["target"], 0)
                    total = objective["count"]
                    progress = f"{current}/{total}"
                    print(colored(f"• {quest['name']}: {progress}", "white"))
            
            # Главное меню
            print(colored("\n▶ ДЕЙСТВИЯ:", "cyan"))
            actions = [
                (1, "Исследовать", "white", "Поиск сокровищ и врагов"),
                (2, "Путешествовать", "white", "Перемещение между локациями"),
                (3, "Магазин", "white", "Купить/продать предметы"),
                (4, "Инвентарь", "white", "Управление предметами"),
                (5, "Персонаж", "white", "Просмотр характеристик"),
                (6, "Задания", "white", "Управление заданиями"),
                (7, "Отдых", "white", "Восстановить ОЗ и ОМ (только в Деревне)"),
                (8, "Сохранить", "green", "Сохранить прогресс"),
                (9, "Выход", "red", "Выход в главное меню")
            ]
            
            half = len(actions) // 2 + len(actions) % 2
            for i in range(half):
                line = colored(f"[{actions[i][0]}] ", "cyan") + colored(actions[i][1], actions[i][2]) + f" - {actions[i][3]}"
                if i + half < len(actions):
                    padding = 35 - len(actions[i][1]) - len(actions[i][3])
                    padding = max(2, padding)
                    line += " " * padding
                    line += colored(f"[{actions[i+half][0]}] ", "cyan") + colored(actions[i+half][1], actions[i+half][2]) + f" - {actions[i+half][3]}"
                print(line)
            
            choice = input("\nВведите ваш выбор (1-9): ")
            
            if choice == "1":
                self.explore()
            elif choice == "2":
                self.travel_menu()
            elif choice == "3":
                self.shop_menu()
            elif choice == "4":
                self.display_inventory()
            elif choice == "5":
                self.display_character_info()
                input("\nНажмите Enter для продолжения...")
            elif choice == "6":
                self.quest_menu()
            elif choice == "7":
                self.rest()
            elif choice == "8":
                self.save_game()
                input("\nНажмите Enter для продолжения...")
            elif choice == "9":
                confirm = input(colored("Вы уверены, что хотите выйти? Несохраненный прогресс будет потерян. (д/н): ", "yellow")).lower()
                if confirm == 'д':
                    break
            else:
                print(colored("\nНеверный выбор. Пожалуйста, попробуйте снова.", "red"))
                input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    try:
        os.system("cls")
        
        print(colored(TITLE_ART, 'yellow'))
        
        # Анимированный текст приветствия
        animate_text("Было сделано Аутистом", color='green')
        animate_text("Под бутылкой хенеси с принглс", color='cyan')
        
        print("\n" + colored("Загрузка игры...", 'yellow'))
        loading_screen("Подготовка RPG окружения", 2)
        
        # Инициализировать и запустить игру
        game = Game()
        game.main_menu()
        
    except KeyboardInterrupt:
        print(colored("\n\nИгра прервана. Спасибо за игру!", "yellow"))
    except Exception as e:
        print(colored(f"\n\nПроизошла ошибка: {str(e)}", "red"))
        # import traceback; traceback.print_exc()
    finally: # Очистка ресурсов
       
        try:
            if 'game' in locals() and hasattr(game, 'listener') and game.listener:
                game.listener.stop()
        except:
            pass
        
        farewell_art = pyfiglet.figlet_format("ДО СВИДАНИЯ!", font="slant")
        print(colored(farewell_art, 'green'))
        print(colored("Благодарим за игру в нашу текстовую RPG!", 'cyan'))
        print(colored("Надеемся, вам понравилось приключение в мире фэнтези!", 'yellow'))
