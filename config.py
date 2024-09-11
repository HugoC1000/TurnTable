from datetime import datetime

SCHEDULE_START = datetime(2024, 9, 4).date()
# Time slots
TIME_SLOTS = ["08:20 - 09:30", "09:35 - 10:45", "-", "11:05 - 12:15", "-", "13:05 - 14:15", "14:20 - 15:30"]

CUSTOM_BLOCK_TIMES = {
    datetime(2024,8,30).date() : ["09:35 - 10:40", 
                                  "-",
                                "10:55 - 11:35", 
                                "11:40 - 12:20",
                                "-",
                                "13:20 - 14:00", 
                                "14:05 - 14:45", 
                                "14:50 - 15:30"],
    datetime(2024,9,3).date() : ["09:35 - 10:40", 
                                 "-",
                          "10:55 - 11:35", 
                          "11:40 - 12:20",
                          "-",
                        "13:20 - 14:00", 
                          "14:05 - 14:45", 
                          "14:50 - 15:30"],
    datetime(2024,9,5).date() : ["08:20 - 09:20", 
                          "09:25 - 10:25", 
                          "-",
                          "10:45 - 11:45",
                        "11:50 - 12:30", 
                        "-",
                          "13:25 - 14:25", 
                          "14:30 - 15:30"],
    datetime(2024,9,6).date() : ["08:20 - 09:20", 
                          "09:25 - 10:25", 
                          "-",
                          "10:45 - 12:10",
                        "-",
                          "13:05 - 14:25", 
                          "14:30 - 15:30"],

}

SCHEDULE_PATTERN = [
    ["1A","1B","1C(A)","1D","1E"],
    ["2A","2B","2C","2D","2E"],
    ["1A","1B","1D","1E","1C(P)"],
    ["2A","2B","2D","2E","2C"],
    ["1A","1B","1E","1C(A)","1D"],
    ["2A","2B","2E","2C","2D"],
    ["1A","1B","1C(P)","1D","1E"],
    ["2A","2B","2C","2D","2E"],
    ["1A","1B","1D","1E","1C(A)"],
    ["2A","2B","2D","2E","2C"],
    ["1A","1B","1E","1C(P)","1D"],
    ["2A","2B","2E","2C","2D"],
]

CUSTOM_BLOCK_ORDERS = {
    datetime(2024,8,30).date(): ["2A","2B","2C","school_event", "2D","2E"],
    datetime(2024,9,3).date(): ["1C(PA)","2A","2B","2C","2D","2E"],
    datetime(2024,9,5).date():["2A","2B","2C","school_event", "2D","2E"],
    datetime(2024,9,6).date():["1A","1B","1C(PA)","1D","1E"],   
    datetime(2024,9,10).date() : ['1A','1B','1E','2E','1D'],
    datetime(2024, 12, 20).date(): ["2A", "1A", "2B", "1B", "2C", "1C(P)", "2D", "1D", "2E", "1E"],
      # Example: Last day before winter break
}

SPECIAL_UNIFORM_DATES = {
    datetime(2024,9,3).date() : "Ceremonial",
    datetime(2024,9,6).date() : "Ceremonial",
    datetime(2024,9,27).date() : "Orange Shirt Day",
    datetime(2024,9,12).date() : "Ceremonial",
    datetime(2024,9,13).date() : "PE Uniform allowed all day. Else, regular uniform"
}

ROOMS_FOR_COURSES = {
    "1A" : {"AP Chinese" : "021W","AP Modern World" : "S 215" , "CLE" : "S 101", "Concert Band 10" : "J 009/Band Room" , "Entrepreneurship 12" : "S 114","PC 12" : "S 013" , "Socials 10" : "S 112" , "Theatre Comp. 10" : "J 013/Drama Room", "Web Dev 10": "S 206/Holowka Room"},
    "1B" : {"AP Calculus BC" : "032E", "CLE" : "034E", "EFP 10" : "S 110" , "French 10 Enr" : "023W" , "French 11" : "021W" , "Lit Studies 11" : "S 112", "Pre-AP Eng. 11" : "S 114", "Science 10" : "S 200", "Socials 10" : "S 122", "Study Block" : "Location varies"},
    "1C" : {"Advisory Field" : "S 013", "Advisory Sjerven" : "S 110" , "Advisory McGee" : "S 112", "Advisory O'Donnell" : "S 122"},
    "1D" : {"AP CSP" : "S 203/Lu's Lab", "Art Studio 10" : "J 010/Art Room", "EFP 10" : "033E", "French 10" : "S 216", "Lit Studies 11" : "S 112", "Pre-AP Eng. 11" : "S 114", "PC 11" : "032E" , "PC 12" : "031E", "Spanish 10" : "024E", "Study Block" : "Location varies","WP" : "S 013"},
    "1E" : {"Chem 11" : "S 200", "CLE" : "034E" , "CLE(WP)" : "S 013" , "Drafting 11" : "J 010/Art Room", "EFP 10" : "032E" , "French 11 Enr" : "S 013", "Mandarin 10 Accel" : "021W" , "Media Design 10" : "S 216", "PE 11" : "Location varies" , "PC 12" : "031E" , "Study Block" : "Location varies"},
    "2A" : {"Active Living 11" : "Location varies" ,"AP Economics" : "S 203/Lu's Lab" , "Chem 11" : "S 200" , "Eng. Studies 12" : "S 108" , "French 10" : "S 013" , "PE 10" : "Location varies" , "PE Aquatics" : "A body of water" ,"PC 11" : "032E" , "Science 10" : "S 208" , "Socials 10" : "S 114" , "Study Block" : "Location varies"},
    "2B" : {"AP Economics" : "S 203/Lu's Lab", "AP French" : "022W", "AP Music Theory" : "J 009/Band Room", "Chem 12" : "S 200", "Life Science 11" : "S 204", "PE 10 Brenko" : "Location varies", "PE 10 Kimura" : "Location varies", "PC 11" : "034E", "Science 10" : "S 208", "Study Block" : "Location varies"},
    "2C" : {"AP Human Geo" : "S 216","AP Stats" : "032E",  "Film/TV 11" : "S 211",  "French 10 Enr" : "023W", "French 11 Enr" : "S 013", "French 12" : "022W",  "Jazz Perf. 11" : "J 009/Band Room", "Math 10" : "033E",  "Mandarin 10" : "021W", "Mandarin 11 Accel" : "021W", "Physics 11" : "S 208", "Pre-AP Eng. 10" : "S 112", "Science 10" : "S 200", "Socials 10" : "S 114", "Study Block" : "Location varies"},
    "2D" : {"Art Studio 10" : "J 010/Art Room", "CLE" : "032E", "Film/TV 11" : "S 221", "Life Science 11" : "S 200", "Pre-AP Eng. 10" : "S 122", "PC 12" : "031E", "Study Block" : "Location varies", "Web Dev 10" : "S 20/Holowka Room"},
    "2E" : {"20 Cent. History" : "S 114", "BC FP 12" : "S 216",  "Chem 11" : "S 200", "French 10" : "S 013", "Math 10" : "031E", "Physics 11" : "S 208", "Physics 12" : "S 206/Holowka Room", "PC 11" : "034E", "Study Block" : "Location varies", "Woodwork 10" : "J 012/Woodshop"}
}

CUSTOM_DAYS_OFF = [datetime(2024, 9, 2).date()]  # Example: holidays
DAYS_OFF = {5, 6}  # Saturday and Sunday

BLOCK_1A_COURSES = ["AP Chinese", "AP Stats", "AP Modern World", "CLE", "Concert Band 10", "Entrepreneurship 12",  "PC 12", "Socials 10","Theatre Comp. 10", "Web Dev 10"]
BLOCK_1B_COURSES = ["AP Calculus BC", "CLE", "EFP 10", "French 10 Enr", "French 11", "Lit Studies 11", "Pre-AP Eng. 11", "Science 10", "Socials 10", "Study Block"]
BLOCK_1C_COURSES = ["Advisory Field", "Advisory Harms", "Advisory McGee", "Advisory O'Donnell", "Advisory Sjerven" ]
BLOCK_1D_COURSES = ["AP CSP", "Art Studio 10", "EFP 10", "French 10", "Lit Studies 11", "Pre-AP Eng. 11",  "PC 11","PC 12", "Spanish 10", "Study Block", "WP"]
BLOCK_1E_COURSES = ["Chem 11", "CLE", "CLE(WP)", "Drafting 11", "EFP 10", "French 11 Enr", "Mandarin 10 Accel", "Media Design 10", "PE 11", "PC 12", "Study Block" ]
BLOCK_2A_COURSES = ["Active Living 11",  "AP Economics", "Chem 11", "Eng. Studies 12", "French 10", "PE 10", "PE Aquatics", "PC 11",  "Science 10", "Socials 10", "Study Block"]
BLOCK_2B_COURSES = ["AP Economics", "AP French", "AP Music Theory", "Chem 12", "Life Science 11", "PE 10 Brenko", "PE 10 Kimura", "PC 11", "Science 10", "Study Block"]
BLOCK_2C_COURSES = ["AP Human Geo","AP Stats",  "Film/TV 11",  "French 10 Enr", "French 11 Enr", "French 12",  "Jazz Perf. 11", "Math 10",  "Mandarin 10", "Mandarin 11 Accel", "Physics 11", "Pre-AP Eng. 10", "Science 10H", "Socials 10", "Study Block"]
BLOCK_2D_COURSES = ["Art Studio 10", "CLE", "Film/TV 11", "Life Science 11", "Pre-AP Eng. 10", "PC 12", "Study Block", "Web Dev 10"]
BLOCK_2E_COURSES = ["20 Cent. History", "BC FP 12",  "Chem 11", "French 10", "Math 10", "Physics 11", "Physics 12", "PC 11", "Study Block", "Woodwork 10"]