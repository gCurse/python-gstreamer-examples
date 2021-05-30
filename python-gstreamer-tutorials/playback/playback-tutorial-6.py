#!/usr/bin/env python3
# https://gstreamer.freedesktop.org/documentation/tutorials/playback/audio-visualization.html

import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst  # noqa E409

# Initialize GStreamer
Gst.init(None)


def filter_vis_features(feature, *args):
    """Return "True" if "feature" is a visualization element"""

    if not isinstance(feature, gi.overrides.Gst.ElementFactory):
        return False
    if "Visualization" not in feature.get_metadata("klass"):
        return False
    return True


def main():
    # Get visualisation-plugins
    vis_list = Gst.Registry.feature_filter(
        Gst.Registry.get(), filter_vis_features, False, None
    )
    # Print visualization-plugins names
    print("Available visualization plugins:\n")
    selected_visualisation = None
    if vis_list:
        for visualisation in vis_list:
            name = visualisation.name
            longname = visualisation.get_longname()
            print(longname)
            # Choose the plugin we want
            if (
                longname.lower().startswith("goo")
                and selected_visualisation is None
            ):
                selected_visualisation = [name, longname]

    # Don't use an empty factory
    if not selected_visualisation:
        print("\nNo visualization plugins found!\n")
        sys.exit(1)
    else:
        print(f"\nChosen: {selected_visualisation[1]}")

    # Get the chosen plugin
    vis_plugin = Gst.ElementFactory.make(
        selected_visualisation[0], "visualisation"
    )

    # Build the pipeline
    uri = "http://radio.hbr1.com:19800/ambient.ogg"
    pipeline = Gst.parse_launch("playbin uri=" + uri)

    # Set the visualization flag
    flags = pipeline.get_property("flags") | 0x00000008
    pipeline.set_property("flags", flags)
    pipeline.set_property("vis-plugin", vis_plugin)

    # start playing
    pipeline.set_state(Gst.State.PLAYING)

    # wait until EOS or error
    bus = pipeline.get_bus()
    msg = bus.timed_pop_filtered(
        Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS
    )
    if msg is not None:
        pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    main()
