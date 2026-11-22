"""The meter driver's stale-frame check, answered by the PanelCamShot stream that is photographing the pour."""


def live(camera):
    if camera is not None:
        camera.live()
