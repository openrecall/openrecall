import pystray
import webbrowser
from PIL import Image

image = Image.open("./images/caret-right-square-fill.png","r")

def after_click(icon, query):
    if str(query) == "openrecall Search":
        webbrowser.open_new_tab('http://127.0.0.1:8082')
    elif str(query) == "openrecall homepage":
        webbrowser.open('https://github.com/openrecall/openrecall',new=2, autoraise=True)
        # icon.stop()
    #elif str(query) == "Exit":
    #    icon.stop()
 
def create_system_tray_icon(): 
    icon = pystray.Icon("GFG", image, "openrecall is recording....", 
                        menu=pystray.Menu(
        pystray.MenuItem("openrecall Website", 
                        after_click),
        pystray.MenuItem("openrecall homepage", 
                        after_click),
        #pystray.MenuItem("Exit", after_click)))
    return icon
 
 