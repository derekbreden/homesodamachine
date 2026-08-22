"""Cut the viewer's assembly-scene GLBs without starting the card-image browser."""

import render_scenes


if __name__ == "__main__":
    render_scenes.main(images=False, glbs=True)
