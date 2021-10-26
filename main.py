'''
Single file script to retrieve data from binary log Blur generates after every race.
'''
import os
import io
import json
from dataclasses import asdict,field,dataclass

bots_names_list = [
    "ajay",
    "bobby",
    "carver",
    "casimiro",
    "drayke",
    "jun",
    "khan",
    "laraya",
    "maaz",
    "morrissey",
    "natalya",
    "no-1",
    "odalis",
    "rhymer",
    "rin",
    "shannon",
]

'''
{'map_name': 'Barcelona Gracia 2', 'number_of_racers': 5, 'laps': 3, 'racers_info': {2: {'player_name': 'Sneakyhydra', 'traveled_distance': 13596.0, 'mod_1_id': 6, 'mod_1_name': 'Stable_Frame', 'mod_2_id': 13, 'mod_2_name': 'Safety_Net', 'mod_3_id': 20, 'mod_3_name': 'Laser_Sight', 'player_level': 2, 'player_legend': 0, 'player_car_name': 'BMW 1 Series Concept Race', 'total_fans': 765, 'starting_pos': 2, 'finish_pos': 2, 'final_state_id': 2, 'final_state': 'Finished'}, 3: {'player_name': 'Morr', 'traveled_distance': 13596.0, 'mod_1_id': 6, 'mod_1_name': 'Stable_Frame', 'mod_2_id': 13, 'mod_2_name': 'Safety_Net', 'mod_3_id': 20, 'mod_3_name': 'Laser_Sight', 'player_level': 1, 'player_legend': 0, 'player_car_name': 'BMW 1 Series Concept Race', 'total_fans': 710, 'starting_pos': 3, 'finish_pos': 3, 'final_state_id': 2, 'final_state': 'Finished'}, 1: {'player_name': 'AlwaysWin', 'traveled_distance': 13596.0, 'mod_1_id': 7, 'mod_1_name': 'Battering_Ram', 'mod_2_id': 13, 'mod_2_name': 'Safety_Net', 'mod_3_id': 19, 'mod_3_name': 'Fan_Favourite', 'player_level': 2, 'player_legend': 0, 'player_car_name': 'BMW 1 Series Concept Race', 'total_fans': 800, 'starting_pos': 1, 'finish_pos': 1, 'final_state_id': 2, 'final_state': 'Finished'}, 5: {'player_name': 'Ish023', 'traveled_distance': 13596.0, 'mod_1_id': 6, 'mod_1_name': 'Stable_Frame', 'mod_2_id': 13, 'mod_2_name': 'Safety_Net', 'mod_3_id': 20, 'mod_3_name': 'Laser_Sight', 'player_level': 1, 'player_legend': 0, 'player_car_name': 'BMW 1 Series Concept Race', 'total_fans': 590, 'starting_pos': 5, 'finish_pos': 5, 'final_state_id': 2, 'final_state': 'Finished'}, 4: {'player_name': 'Raaghavdubey', 'traveled_distance': 13596.0, 'mod_1_id': 6, 'mod_1_name': 'Stable_Frame', 'mod_2_id': 13, 'mod_2_name': 'Safety_Net', 'mod_3_id': 20, 'mod_3_name': 'Laser_Sight', 'player_level': 1, 'player_legend': 0, 'player_car_name': 'BMW 1 Series Concept Race', 'total_fans': 535, 'starting_pos': 4, 'finish_pos': 4, 'final_state_id': 2, 'final_state': 'Finished'}}}
'''

@dataclass
class blur_racer_data:
    player_name: str
    player_level: int
    player_legend: int
    total_fans: int

    player_car_id: int
    player_car_name: str

    starting_pos: int
    finish_pos: int

    final_state: int #2 - Finished

    traveled_distance: float

    mod_1_id: int
    mod_1_name: str
    mod_2_id: int
    mod_2_name: str
    mod_3_id: int
    mod_3_name: str


@dataclass
class blur_race_data:
    map_name: str
    race_mode: int
    racers: int
    laps: int
    racers_data: list[blur_racer_data] = field(default_factory=list)
    race_mode: int = 0
    city_id: int = 0
    time_limit:int=0



class blur_racelog_parser:
    def __init__(self):
        self.log_reader: io.BytesIO
        with open('maps.json') as json_file:
            self.map_data = json.load(json_file)

        with open('cars.json') as json_file:
            self.car_data = json.load(json_file)

    def get_mod_name(self,mod_id:int)-> str:
        mods_data = {
            1: "iron_fist",
            2: "jump_the_gun",
            3: "front_runner",
            4: "drifter",
            5: "titanium_armour",
            6: "showy_flourish",
            7: "stable_frame",
            8: "battering_ram",
            9: "decoy_drop",
            10: "road_sweeper",
            11: "scrambler",
            12: "splash_damage",
            13: "shielding_efficiency",
            14: "safety_net",
            15: "shielded_boosters",
            16: "shielded_bay",
            17: "ecm",
            18: "vampiric_wreck",
            19: "bribe",
            20: "fan_favourite",
            21: "laser_sight",
            22: "advanced_radar",
            23: "silent_running",
            24: "last_gasp",
            25: "mastermine",
            26: "additionalblindfireshots",
            27: "additionalshockdomes",
            28: "doubleshield",
            29: "fansnitrogift",
            30: "nitrorift",
            31: "repairbonus",
            32: "shotgunblindfire",
            33: "shuntdamage",
        }

        if mod_id+1 in mods_data: #ids in multiplayer.bin are n+1 from logs data. Will stick to .bin values.
            return mods_data[mod_id+1]
        elif mod_id == 4294967295: #FFFFFFFF
            return "none"
        else:
            return "unknown"

    def get_game_type_name(game_type_id: int) -> str:

        game_types = {
            24392580: "community_event",
            2366728894: "team_racing",
            3468808035: "motor_mash",
            1647796835: "powered_up_racing",
            1786934394: "skirmish_racing"
        }

        if game_type_id in game_types:
            return game_types[game_type_id]
        else:
            return "unknown"

    def parse_log(self,log_data:bytes)->dict:
        pass
