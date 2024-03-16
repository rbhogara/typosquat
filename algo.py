from cmd import Cmd
import homoglyphs as hg
from metaphone import doublemetaphone
import Levenshtein as lev
from itertools import combinations
import os
from pymongo import MongoClient


class word:  
    def __init__(self):      
        self.word = None
        self.meaning="None"
        self.next = None
class Node:  
    def __init__(self):      
        self.words = word()
        self.alphabet=""
        self.count = None
        self.next = None
        self.prev = None 
class Prompt(Cmd):
    prompt = 'typosquat>'
    intro = """ """
    def __init__(self, *args, **kwargs):
        self.protected_domains=[]
        self.current_directory = os.getcwd()
        self.user_entered_domain=""
        self.db=self.get_db()
        super().__init__(*args, **kwargs)
    def get_db(self):
        client = MongoClient("mongodb://typosqat:26eed7499d45391e9f5f3fa2b20de2f445a6a717@bdb-int-prod-mongos-1.cisco.com:27017/?authSource=task_typosqat&readPreference=secondary&tls=true&tlsAllowInvalidCertificates=true")  
        db = client["task_typosqat"]
        return db
    def generate_typo(self,word):
        typos = []
        keyboard_layout = {
        'a': ['q', 'w', 's', 'z'],
        'b': ['v', 'g', 'h', 'n'],
        'c': ['x', 'd', 'f', 'v'],
        'd': ['s', 'e', 'r', 'f', 'c', 'x'],
        'e': ['w', 's', 'd', 'r', '3', '4'],
        'f': ['d', 'r', 't', 'g', 'v', 'c'],
        'g': ['f', 't', 'y', 'h', 'b', 'v'],
        'h': ['g', 'y', 'u', 'j', 'n', 'b'],
        'i': ['u', 'j', 'k', 'o', '8', '9'],
        'j': ['h', 'u', 'i', 'k', 'm', 'n'],
        'k': ['j', 'i', 'o', 'l', 'm'],
        'l': ['k', 'o', 'p'],
        'm': ['n', 'j', 'k'],
        'n': ['b', 'h', 'j', 'm'],
        'o': ['i', 'k', 'l', 'p', '9', '0'],
        'p': ['o', 'l', '0'],
        'q': ['1', '2', 'w', 'a'],
        'r': ['e', 'd', 'f', 't', '4', '5'],
        's': ['w', 'e', 'd', 'x', 'z', 'a'],
        't': ['r', 'f', 'g', 'y', '5', '6'],
        'u': ['y', 'h', 'j', 'i', '7', '8'],
        'v': ['c', 'f', 'g', 'b'],
        'w': ['q', 'a', 's', 'e', '2', '3'],
        'x': ['z', 's', 'd', 'c'],
        'y': ['t', 'g', 'h', 'u', '6', '7'],
        'z': ['a', 's', 'x'],
        '1': ['q', '2'],
        '2': ['1', '3', 'w', 'q'],
        '3': ['2', '4', 'e', 'w'],
        '4': ['3', '5', 'r', 'e'],
        '5': ['4', '6', 't', 'r'],
        '6': ['5', '7', 'y', 't'],
        '7': ['6', '8', 'u', 'y'],
        '8': ['7', '9', 'i', 'u'],
        '9': ['8', '0', 'o', 'i'],
        '0': ['9', 'p', 'o'],
        '-': ['0', '='],
        '=': ['-'],
        ';': ['l', "'"],
        "'": [';', 'l'],
        ',': ['m', 'n', '.'],
        '.': [',', 'm', '/'],
        '/': ['.', ',']
        }
        
        # Missing letter
        if len(word) > 1:
            typos.append(word[:-1])  # Remove last letter
            typos.append(word[1:])   # Remove first letter
            typos.append(word[0:len(word)//2] + word[len(word)//2+1:])  # Remove middle letter

        # Extra letter (duplicates the last letter for simplicity)
        typos.append(word + word[-1])

        # Swapping adjacent letters
        if len(word) > 1:
            for i in range(len(word) - 1):
                typo = list(word)
                typo[i], typo[i+1] = typo[i+1], typo[i]
                typos.append(''.join(typo))

        # Replacing a letter with a nearby key
        for i, letter in enumerate(word):
            if letter in keyboard_layout:
                adjacent_keys = keyboard_layout[letter]
                
                # Generate combinations for 1, 2, or 3 adjacent key replacements
                for r in range(1, 7):  # r is the number of adjacent letters to consider
                    for combo in combinations(adjacent_keys, r):
                        # Replace letter with each combination (join for more than one letter)
                        replacement = ''.join(combo)
                        typo = word[:i] + replacement + word[i+1:]
                        typos.append(typo)
                        
                        # For combinations with more than one letter, consider inserting instead of replacing
                        if r > 1:
                            typo_insert = word[:i] + replacement + word[i:]
                            typos.append(typo_insert)

        
        return list(set(typos))  # Remove duplicates

    def do_modelling(self,arg):
        domain_names=input("Comma Seperated Domain list to protect:")
        self.protected_domains=[domain.lower().strip() for domain in domain_names.split(',')]
        # homoglyphs = hg.Homoglyphs(categories=('BRAILLE', 'CYRILLIC', 'PALMYRENE', 'ORIYA', 'HIRAGANA', 'KAYAH_LI', 'SIGNWRITING', 'BHAIKSUKI', 'THAI', 'GOTHIC', 'BENGALI', 'BAMUM', 'LIMBU', 'MRO', 'SHARADA', 'TAI_LE', 'TAKRI', 'LYDIAN', 'SUNDANESE', 'KHMER', 'MEROITIC_HIEROGLYPHS', 'HANIFI_ROHINGYA', 'NANDINAGARI', 'PAU_CIN_HAU', 'HANUNOO', 'MAKASAR', 'BUGINESE', 'JAVANESE', 'BATAK', 'COMMON', 'SAMARITAN', 'CHAKMA', 'TANGUT', 'MEROITIC_CURSIVE', 'AVESTAN', 'ANATOLIAN_HIEROGLYPHS', 'TIRHUTA', 'LINEAR_A', 'CHAM', 'GRANTHA', 'ARABIC', 'SAURASHTRA', 'COPTIC', 'KANNADA', 'MIAO', 'LINEAR_B', 'NABATAEAN', 'GUJARATI', 'CUNEIFORM', 'OLD_SOUTH_ARABIAN', 'NUSHU', 'HATRAN', 'PHAGS_PA', 'OLD_PERSIAN', 'YI', 'SYLOTI_NAGRI', 'DUPLOYAN', 'DESERET', 'SHAVIAN', 'KHAROSHTHI', 'GEORGIAN', 'MARCHEN', 'OLD_NORTH_ARABIAN', 'OLD_SOGDIAN', 'OSAGE', 'SINHALA', 'WARANG_CITI', 'AHOM', 'TELUGU', 'SOGDIAN', 'MALAYALAM', 'MANDAIC', 'OLD_PERMIC', 'BALINESE', 'BASSA_VAH', 'BRAHMI', 'CAUCASIAN_ALBANIAN', 'NYIAKENG_PUACHUE_HMONG', 'VAI', 'INHERITED', 'ADLAM', 'MANICHAEAN', 'CYPRIOT', 'MODI', 'DEVANAGARI', 'RUNIC', 'TAGBANWA', 'LAO', 'LATIN', 'TAI_THAM', 'NKO', 'NEW_TAI_LUE', 'SOYOMBO', 'IMPERIAL_ARAMAIC', 'OSMANYA', 'ELBASAN', 'LYCIAN', 'OLD_TURKIC', 'CARIAN', 'PAHAWH_HMONG', 'THAANA', 'REJANG', 'HANGUL', 'TAGALOG', 'CHEROKEE', 'MEDEFAIDRIN', 'KHUDAWADI', 'ARMENIAN', 'INSCRIPTIONAL_PAHLAVI', 'TAI_VIET', 'OL_CHIKI', 'EGYPTIAN_HIEROGLYPHS', 'OLD_HUNGARIAN', 'PHOENICIAN', 'UGARITIC', 'LEPCHA', 'SYRIAC', 'ETHIOPIC', 'MONGOLIAN', 'MEETEI_MAYEK', 'GREEK', 'MASARAM_GONDI', 'SIDDHAM', 'BUHID', 'BOPOMOFO', 'KATAKANA', 'ZANABAZAR_SQUARE', 'OLD_ITALIC', 'MULTANI', 'CANADIAN_ABORIGINAL', 'HAN', 'TIBETAN', 'DOGRA', 'MYANMAR', 'NEWA', 'TIFINAGH', 'WANCHO', 'ELYMAIC', 'GURMUKHI', 'OGHAM', 'GLAGOLITIC', 'PSALTER_PAHLAVI', 'MAHAJANI', 'GUNJALA_GONDI', 'MENDE_KIKAKUI', 'KAITHI', 'LISU', 'HEBREW', 'INSCRIPTIONAL_PARTHIAN', 'SORA_SOMPENG',  'KHOJKI'))  # alphabet loaded here
        homoglyphs = hg.Homoglyphs(categories=('LATIN', 'COMMON', 'CYRILLIC'))
        for domain in self.protected_domains:
            if os.path.exists(self.current_directory+'/homoglyph/'+domain+'.txt'):
                continue
            with open(self.current_directory+'/homoglyph/'+domain+'.txt', 'w+') as file:
                for i in homoglyphs.get_combinations(domain):
                    file.write(i + '\n')
            # if 'hg_'+domain in self.db.list_collection_names():
            #     continue
            # else:
            #     for i in homoglyphs.get_combinations(domain):
            #         self.db['hg_'+domain].insert_one({'u':i})
            # self.homoglyphs_domains = self.homoglyphs_domains + homoglyphs.get_combinations(domain)
        for domain in self.protected_domains:
            if os.path.exists(self.current_directory+'/butterfinger/'+domain+'.txt'):
                continue
            with open(self.current_directory+'/butterfinger/'+domain+'.txt', 'w+') as file:
                for i in self.generate_typo(domain):
                    file.write(i + '\n')
            
    def do_check(self,input_str):
        print("*"*50)
        print("Verdict from D-Metaphone:")
        D_Metaphone_flag = False
        self.user_entered_domain=input_str.lower().strip()
        word1_encodings = doublemetaphone(self.user_entered_domain)
        for domain in self.protected_domains:
            word2_encodings = doublemetaphone(domain)
            if (any(encoding in word2_encodings for encoding in word1_encodings if encoding)):
                print(f"Verdict: True")
                D_Metaphone_flag = True
        if not D_Metaphone_flag:
            print("Verdict: False")
        print("*"*50)
        print("*"*50)
        print("Verdict from Levenshtein:")

        lev_flag= False
        for domain in self.protected_domains:
            distance = lev.distance(self.user_entered_domain, domain)
            if len(domain) >= 5:
                threshold=3
            else:
                threshold=len(domain)//2
            if distance <= threshold:
                print(f"Verdict: {distance <= threshold}")
                lev_flag = True
        if not lev_flag:
            print("Verdict: False")
        print("*"*50)
        print("*"*50)
        print("Verdict from Homoglyph")
        hg_flag=False
        for domain in self.protected_domains:
            file_path = os.path.join(self.current_directory+'/homoglyph/', domain+".txt")
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    for line_number, line in enumerate(file, start=1):
                        if self.user_entered_domain == line.strip():
                            print("Verdict : True")
                            hg_flag = True
                            break
                    if hg_flag:
                        break                        
        if not hg_flag:
            print("Verdict: False")
        print("*"*50)
        print("*"*50)
        print("Verdict from ButterFinger")
        butter_flag= False
        for domain in self.protected_domains:
            file_path = os.path.join(self.current_directory+'/butterfinger/', domain+".txt")
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    butter_contents = file.read()
                    if self.user_entered_domain in butter_contents:
                        butter_flag = True
                        print("Verdict : True")
                        break
        if not butter_flag:
            print("Verdict: False")     
        print("*"*50)
    def do_bye(self, arg):
        return True
    def help_modelling(self):
        print("Enter the domain names to protect")

    def help_check(self):
        print("Check if the user entered domain is typosquatted with given domain")
    

        
def main():
    Prompt().cmdloop()


if __name__ == "__main__":
    main()