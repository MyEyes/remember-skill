# Copyright 2018 Lukas Gangel
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import traceback
import logging
import re

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
from mycroft.audio import wait_while_speaking 
from mycroft.util.log import getLogger
from .information_store import LocalFileInformationStore

logger = getLogger(__name__)


__author__ = 'MyEyes'

class rememberSkill(MycroftSkill):

    def __init__(self):
        super(rememberSkill, self).__init__(name="rememberSkill")
        self.information_store = LocalFileInformationStore(self.file_system.path+"/rememberlist.txt")
            
    @intent_handler(IntentBuilder("WhatToRememberIntent").require("Did").require("You").require("Remember").build())
    def WhatToRememberIntent(self, message): # user wants to know what we've got
        try: # try to open our remember list readonly and give user all phrases
            alist = self.information_store.retrieve_info()
            if len(alist)==0:
               self.speak_dialog("sorry") # we got nothing in our list
            else: # we got something
               rememberphrases = " and ".join(alist)
               self.speak_dialog('iremembered', {'REMEMBER': rememberphrases}) # give the user our nice list
        except:
            self.speak_dialog("sorry") # oh damn, something happened
        
    @intent_handler(IntentBuilder("RememberIntent").require("Remember").require("WhatToRemember").build())
    def RememberIntent(self, message): # user wants us to remember something
        utt=(message.data.get("utterance"))
        if re.match("what did you", utt) is not None: # workaround for what did you remember?
           self.WhatToRememberIntent(message)
           return None
        rememberPhrase = message.data.get("WhatToRemember", None) # get phrase user wants us to remember
        try: # if user said something like "remember phrase get some milk" we don't want phrase to be saved, brakes skill a bit, we don't wanna skill broken, we like skill
            rememberPhrase = rememberPhrase.replace('phrase ', '') # Phrase Evanesca! if you got this reference, you should stop reading comments in code and go out a bit, have fun with friends or watch birds or something like that
        except:
            pass #go on if the user does not put phrase in the phrase, in the phrase, in the phrase.... phraseception
        try: # lets try to remember
            if rememberPhrase: # we need a phrase to remember
               if len(rememberPhrase) > 4: # phrase should be at least 5 characters
                  self.information_store.store_info(rememberPhrase)
                  self.speak_dialog('gotphrase', {'REMEMBER': rememberPhrase}) # tell user we did it and be proud, good boy mycroft... or girl... what is mycroft? NOTE: make gender-skill
               else: # oh oh, was the phrase to short
                  self.speak_dialog("short") # tell user to stop giving us short messages, we like to talk
        except Exception as e: # error error, we hate errors...
            logging.error(traceback.format_exc())
            self.speak_dialog('sorry') # ... but we are always sorry
    
    @intent_handler(IntentBuilder("DeleteIntent").require("Forget").require("Phrase").optionally("RememberPhrase").optionally("All").build())
    def DeleteIntent(self, message): # function for forgetting/deleting phrases from the list
        rememberPhrase = message.data.get("RememberPhrase", None) # get phrase from spoken sentence
        delall = message.data.get("All", None) # check if there is ALL in the sentence, maybe user wants to clear the complete list
        if delall:
            should_deleteall = self.ask_user_confirm('deleteall') # ask user if we should delete the whole list
            if should_deleteall:# if user said yes 
                try: # try to delete the whole list
                    self.information_store.remove_info()
                    self.speak_dialog("forgotten") # we did forget
                except Exception as e:
                    logging.error(traceback.format_exc())
                    self.speak_dialog('sorryforget') # oh damn -> error
                return None
        #Query info store to see if any information matches
        info = self.information_store.retrieve_info(rememberPhrase)
        if len(info) == 0:
            self.speak_dialog('sorrynophrase') # sorry we couldn't do it
        else:
            should_delete = False
            if len(info) == 1:
                should_delete = self.ask_user_confirm('delete', {'PHRASE': info[0]})
            else:
                should_delete = self.ask_user_confirm('deleteMulti', {'NUMBER': len(info)})
            if should_delete:
                try:
                    self.information_store.remove_info(rememberPhrase)
                    self.speak_dialog("forgotten")
                except:
                    logging.error(traceback.format_exc())
                    self.speak_dialog('sorryforget') # sorry we couldn't do it
            else:
                self.speak_dialog("holdon")

    def ask_user_confirm(self, phrase, args=None):
        response = self.get_response(phrase, args)
        yes_words = set(self.translate_list('yes')) # get list of confirmation words
        resp_split = response.split() 
        if any(word in resp_split for word in yes_words): # if user said yes
            return True
        return False

    def shutdown(self):
        super(rememberSkill, self).shutdown()

    def stop(self):
        pass

def create_skill():
    return rememberSkill()
