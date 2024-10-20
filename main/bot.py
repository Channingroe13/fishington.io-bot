import cv2  # No need for `from cv2 import cv2`
import mss
import numpy as np
import os
import time
from pynput import mouse, keyboard
import random
import pyautogui  # Replace pydirectinput with pyautogui for cross-platform compatibility

class Fisher:
    def __init__(self):
        self.stc = mss.mss()

        path = os.path.dirname(os.path.dirname(__file__))
        self.img_path = os.path.join(path, 'img')
        self.mouse = mouse.Controller()
        self.keyboard = keyboard.Controller()

        self.bar_top = 0
        self.bar_left = 0

        # Increase this limit if you have a larger basket
        self.fish_count = 0
        self.fish_limit = 6
        
        self.keep_fishing = True
        
        # Adding spot to update sell thresholds!
        self.sell_threshold = .8

    def fish(self):
        while self.keep_fishing:
            if self.close_caught_fish():
                # We caught a fish
                self.fish_count += 1
                print(f"Fish Count: {self.fish_count}")
            if self.is_bobber():
                print("FISH on SLEEPING!")
                time.sleep(10)
                continue
            if self.fish_count >= self.fish_limit:
                self.Sell_Fish()
                continue
            # Reset click
            jitter = random.randint(-25, 25)
            cast_jitter = random.random()
            pyautogui.click(800 + jitter, 800 + jitter)  # Replaced pydirectinput with pyautogui
            time.sleep(1)
            self.Click_Location(800 + jitter, 800 + jitter, .2 + cast_jitter)
            print("Throwing line")
            time.sleep(11)
            self.Click_Location(800 + jitter, 800 + jitter, .5)
            time.sleep(.5)

    def is_bobber(self):
        img = self.Screen_Shot()
        bobber_img = cv2.imread(os.path.join(self.img_path, 'bobber.jpg'), cv2.IMREAD_COLOR)
        result_try = cv2.matchTemplate(img, bobber_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result_try)
        return max_val > .9

    def Set_Bobber(self):
        while True:
            print("Reset Click.")
            pyautogui.click(800, 800)
            time.sleep(.6)
            self.Click_Location(800, 800, 1)
            time.sleep(11)
            pyautogui.click(800, 800)
            time.sleep(.6)
            print("Finding Bobber")
            img = self.Screen_Shot()
            bobber_img = cv2.imread(os.path.join(self.img_path, 'bobber.jpg'), cv2.IMREAD_COLOR)
            result_try = cv2.matchTemplate(img, bobber_img, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result_try)
            if max_val > .9:
                print("Found it!!")
                new_max = max_loc
                bar_top = new_max[1] - 20
                bar_left = new_max[0]
                return bar_left, bar_top
            print(f"Current Max: {max_val} sleeping")

    def close_caught_fish(self):
        max_loc, max_val = self.Template_Match("YellowX.jpg", self.Screen_Shot())
        if max_val > .9:
            print("Pushing YellowX")
            self.Click_Location(max_loc[0] + 10, max_loc[1] + 10)
            self.Click_Location(max_loc[0] + 5, max_loc[1] + 5)
            return True
        return False

    def Sell_Fish(self):
        # Get to store if we are not there...
        self.keyboard.press(keyboard.Key.up)
        time.sleep(8)
        self.keyboard.release(keyboard.Key.up)

        self.keyboard.press(keyboard.Key.space)
        time.sleep(1)
        self.keyboard.release(keyboard.Key.space)

        max_loc, max_val = self.Template_Match("SellBox.jpg", self.Screen_Shot())
        if max_val > self.sell_threshold:
            print("We got fish to sell!")
            self.Click_Location(max_loc[0] + 20, max_loc[1] + 30)

            # Look for sell button
            time.sleep(1)
            print("Looking for sell")
            max_loc, max_val = self.Template_Match("SellFor.jpg", self.Screen_Shot())
            if max_val > self.sell_threshold:
                print("Pushing Sell")
                self.Click_Location(max_loc[0] + 40, max_loc[1] + 10)
                time.sleep(1)
                print("Looking for sell Green")
                max_loc, max_val = self.Template_Match("Sell.jpg", self.Screen_Shot())
                while max_val > self.sell_threshold:
                    print("Pushing Sell Green")
                    self.Click_Location(max_loc[0] + 10, max_loc[1] + 10)
                    time.sleep(1)
                    max_loc, max_val = self.Template_Match("Sell.jpg", self.Screen_Shot())
                    time.sleep(1)
                    self.fish_count = 0

        self.Click_Location(200, 500)
        self.Click_Location(200, 500)
        time.sleep(1)
        self.Click_Location(100, 500)
        # Go back fishing...
        self.keyboard.press(keyboard.Key.down)
        time.sleep(8)
        self.keyboard.release(keyboard.Key.down)
        self.keyboard.press(keyboard.Key.down)
        time.sleep(2)
        self.keyboard.release(keyboard.Key.down)

    def Screen_Shot(self, left=0, top=0, width=1920, height=1080):
        stc = mss.mss()
        scr = stc.grab({
            'left': left,
            'top': top,
            'width': width,
            'height': height
        })

        img = np.array(scr)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # Correct color conversion
        return img

    def Template_Match(self, needle, haystack):
        sell_box_img = cv2.imread(os.path.join(self.img_path, needle), cv2.IMREAD_COLOR)
        result_try = cv2.matchTemplate(haystack, sell_box_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result_try)
        return max_loc, max_val

    def Click_Location(self, x, y, wait=0):
        pyautogui.moveTo(x, y)
        pyautogui.mouseDown()
        time.sleep(wait)
        pyautogui.mouseUp()

    def start_fresh(self):
        time.sleep(5)
        self.keyboard.press(keyboard.Key.ctrl)
        self.keyboard.press('r')
        time.sleep(1)
        self.keyboard.release(keyboard.Key.ctrl)
        self.keyboard.release('r')
        time.sleep(1)
        self.keyboard.press(keyboard.Key.enter)
        self.keyboard.release(keyboard.Key.enter)

# Test our classes and functions
if __name__ == "__main__":
    print("Unless you're testing, run main.py")
    fisher = Fisher()
    time.sleep(5)
    fisher.Sell_Fish()
