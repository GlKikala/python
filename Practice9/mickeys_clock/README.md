# Mickey's Clock

Digital-style clock using Mickey Mouse hand graphics.

## Features
- Displays **minutes** and **seconds** only
- **Right hand** → minutes hand
- **Left hand**  → seconds hand
- Smooth, real-time animation (60 fps)
- Procedural white-glove hands if no image found

## Image setup
Place a file named `mickey_hand.png` in your chosen images folder.  
At startup a **folder picker dialog** opens so you can point to any folder
inside the project. The mirrored left-hand is generated automatically.

## Controls
| Key | Action |
|-----|--------|
| **F** | Reopen folder picker to reload images at runtime |
| **ESC** | Quit |

## Requirements
```
pip install pygame
```

## Run
```bash
python main.py
```
