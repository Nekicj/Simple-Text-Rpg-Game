# 🎮 RPGame - Text-Based Fantasy Adventure

![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.6%2B-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

<div align="center">
  <img src="assets/title_banner.png" alt="RPGame Banner" width="600">
  <p><i>A rich text-based RPG adventure with colorful terminal graphics</i></p>
</div>

## 📖 Overview

**RPGame** is an immersive text-based RPG built in Python that brings a classic gaming experience to your terminal. Journey through various locations, battle enemies, complete quests, manage your inventory, and level up your character in this fantasy adventure.

The game features a rich combat system, character progression, equipment management, and a quest system all wrapped in a colorful, animated terminal interface.

## ✨ Features

- **🧙‍♂️ Three distinct character classes**: Warrior, Mage, and Archer
- **⚔️ Strategic combat system** with special abilities and critical hits
- **🌍 Multiple immersive locations** to explore with ASCII art representations
- **📜 Quest system** with objectives, progress tracking, and rewards
- **💰 In-game economy** with a shop for buying and selling items
- **🎒 Inventory management** with equippable items and consumables
- **📈 Character progression** with level-ups and stat improvements
- **💾 Save/load game system** for continuing your adventure
- **🎭 Rich narrative elements** and character interactions
- **🎨 Colorful terminal graphics** with animations and visual effects

## 🚀 Installation

### Prerequisites

Make sure you have Python 3.6+ installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/rpgame.git
   cd rpgame
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Or install dependencies manually:
   ```bash
   pip install pyfiglet termcolor tqdm colorama pynput
   ```

3. Run the game:
   ```bash
   python RPGame.py
   ```

## 📋 Dependencies

The game relies on the following Python libraries:

- **pyfiglet**: For ASCII art text generation
- **termcolor**: For colorful terminal output
- **tqdm**: For progress bars and loading animations
- **colorama**: For cross-platform colored terminal text
- **pynput**: For keyboard input handling

## 🎮 Game Controls and Mechanics

### Main Menu

- **New Game**: Start a new adventure
- **Load Game**: Continue a previously saved game
- **Exit**: Quit the game

### In-Game Commands

Navigate through the game using the numbered options:

- **1. Explore**: Search for treasures and encounters in your current location
- **2. Travel**: Move between different locations
- **3. Shop**: Buy or sell items (available in the Village)
- **4. Inventory**: Manage your items and equipment
- **5. Character**: View your character's stats and equipment
- **6. Quests**: View active quests and their progress
- **7. Rest**: Restore HP and MP (only in the Village)
- **8. Save**: Save your current progress
- **9. Exit**: Return to main menu

## 🧙‍♂️ Character Classes and Features

### Classes

1. **Warrior**
   - High HP and strength
   - Low mana
   - Special Ability: Powerful Strike

2. **Mage**
   - High mana, low HP
   - Magical abilities
   - Special Ability: Fireball

3. **Archer**
   - Balanced stats with high agility
   - Critical hit specialist
   - Special Ability: Precise Shot

### Character Stats

- **HP**: Health Points (reduced when taking damage)
- **MP**: Mana Points (used for special abilities)
- **Strength**: Determines attack power
- **Defense**: Reduces damage taken
- **Agility**: Affects dodge chance and attack order
- **Critical**: Chance to land a critical hit
- **Luck**: Improves various chance-based mechanics

## 🗺️ Locations

The game features several distinct locations to explore:

1. **Village**
   - Safe starting area
   - Contains shops and quest givers
   - Low chance of enemy encounters

2. **Forest**
   - Contains wolves and goblins
   - Moderate danger level
   - Source of basic loot

3. **Mountain Pass**
   - Home to orcs and trolls
   - Higher danger level
   - Better rewards

4. **Ancient Ruins**
   - Contains skeletons and dark mages
   - Highest danger level
   - Best loot and quest opportunities

Each location has its own ASCII art representation and unique enemy encounters.

## ⚔️ Combat System

Battles in RPGame are turn-based with strategic options:

1. **Basic Attack**: Standard damage based on strength
2. **Special Attack**: Class-specific attack using MP
   - Warrior: Powerful Strike (high damage, ignores some defense)
   - Mage: Fireball (magical damage, chance to apply burn effect)
   - Archer: Precise Shot (increased critical hit chance)
3. **Use Potion**: Consume items to restore HP or MP
4. **Flee**: 50% chance to escape combat

Combat features include:
- Critical hits
- Dodge mechanics
- Status effects (burn, poison)
- Enemy-specific attack patterns
- Animated battle effects

## 📜 Quest System

The game includes a quest system with:

- **Multiple quest types**: Primarily combat-focused objectives
- **Progress tracking**: The game tracks your progress toward each objective
- **Rewards**: Experience points, gold, and unique items
- **Quest log**: View your active and completed quests

Examples of quests include:
- Defeat 3 goblins threatening the village
- Clear the forest of wolves
- Defeat the dark mage who is corrupting the land
- Explore ancient ruins and defeat the hidden evil

## 📸 Screenshots

<div align="center">
  <p><i>Screenshots coming soon!</i></p>
  <!-- 
  <img src="screenshots/combat.png" alt="Combat Screenshot" width="400">
  <img src="screenshots/inventory.png" alt="Inventory Screenshot" width="400">
  <img src="screenshots/village.png" alt="Village Screenshot" width="400">
  -->
</div>

## 🤝 Contributing

Contributions are welcome! If you'd like to improve RPGame, feel free to fork the repository and submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Credits

- **Game Developer**: [Your Name]
- **ASCII Art**: Generated using pyfiglet and custom designs
- **Special Thanks**: To all contributors and testers

## 📧 Contact

- GitHub: [@Nekicj](https://github.com/Nekicj)
- Email: [your.email@example.com](mailto:your.email@example.com)

---

<div align="center">
  <p>Made with ❤️ and Python</p>
  <p>© 2025 RPGame</p>
</div>

