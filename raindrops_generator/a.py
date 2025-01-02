from nuscenes.can_bus.can_bus_api import NuScenesCanBus
nusc_can = NuScenesCanBus(dataroot='/home/yoshi-22/UniAD/data/nuscenes/can_bus')

scene_name = 'scene-0001'
nusc_can.print_all_message_stats(scene_name)
message_name = 'steeranglefeedback'
key_name = 'value'
nusc_can.plot_message_data(scene_name, message_name, key_name)

