import { Config } from "@remotion/cli/config";

// Stills as PNG (crisp linework); video frames as JPEG for speed.
Config.setVideoImageFormat("jpeg");
Config.setStillImageFormat("png");
Config.setOverwriteOutput(true);
Config.setChromiumOpenGlRenderer("angle");
