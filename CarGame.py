from tkinter import *
from tkinter.ttk import *
from tkinter.simpledialog import askstring
import random
from PIL import Image , ImageTk

class MainMenu():
    def __init__(self, window):
        self.window = window
        self.loaded_game = None
        

  
        # Load the background image
        image = Image.open("bg.png") #Image by brgfx on Freepik : "https://www.freepik.com/free-vector/aerial-view-garden_4709043.htm#query=8%20bit%20road%20background%20top%20view&position=0&from_view=search&track=ais&uuid=039ca1f6-d56e-4caa-9241-d3e2e8775097" 
        image = image.resize((1280, 720))  # resize image as it is too large
        self.img = ImageTk.PhotoImage(image)

        self.img_label = Label(window, image=self.img)
        self.img_label.image = self.img
        self.img_label.place(x=0, y=0)  # placing image at x = 0 and y = 0

        self.menu_buttons()
    
    def menu_buttons(self):
        style = Style()

        style.configure('TButton', font=('calibri', 20, 'bold'), borderwidth='4')

        style.map('TButton', foreground=[('active', '!disabled', 'green')])

        #Create menu buttons
        start_button = Button(self.window, text="Start", style='TButton', command=self.start_game)
        load_button = Button(self.window, text="Load", style='TButton', command=self.load_game)
        Ld_button = Button(self.window, text="Leader Board", style='TButton', command=self.leaderboard)
        define_button = Button(self.window, text='Customise', style='TButton',command = self.define_keys)
        quit_button = Button(self.window, text="Quit", style='TButton', command=self.window.destroy)

        # Place buttons in the center
        start_button.place(relx=0.5, rely=0.4, anchor=CENTER)
        load_button.place(relx=0.5,rely=0.5, anchor=CENTER)
        Ld_button.place(relx=0.5, rely=0.6, anchor=CENTER)
        define_button.place(relx=0.5, rely=0.7, anchor=CENTER)
        quit_button.place(relx=0.5, rely=0.8, anchor=CENTER)

    def start_game(self):
        #Start the Game
        if self.loaded_game is None:
            self.loaded_game = CarGame(self.window)
        self.loaded_game.run_game()


    def load_game(self):
        #Load saved game
        try:
            with open('savedGame.txt', 'r') as file:
                # Read player's score
                score = int(file.readline().strip())

                # Read player's position
                player_coords = list(map(float, file.readline().strip().split(',')))

        except FileNotFoundError:
            print("No saved game found.")
        
        if self.loaded_game is None:
                self.loaded_game = CarGame(self.window)
        self.loaded_game.load_data(score, player_coords)
    
    def define_keys(self):
         # Open a dialog to let the player define new keys
        left_key = askstring("Define Key", "Enter the new key for Left:")
        right_key = askstring("Define Key", "Enter the new key for Right:")
        up_key = askstring("Define Key", "Enter the new key for Up:")
        down_key = askstring("Define Key", "Enter the new key for Down:")
        
        # Start game with the saved keys
        if self.loaded_game is None:
                self.loaded_game = CarGame(self.window)
        self.loaded_game.load_saved_keys  (left_key, right_key , up_key , down_key)

        
    
    
    def leaderboard(self):

        # Show the leaderboard

        leaderboard_window = Toplevel(self.window)
        leaderboard_window.title("Leaderboard")
        

        leaderboard_canvas = Canvas(leaderboard_window, width=400, height=300, bg='black')
        leaderboard_canvas.pack()

        # Load leaderboard file

        try:
            with open('leaderboard.txt', 'r') as file:
                leaderboard_data = file.readlines()

                leaderboard_data.sort(key=lambda line: int(line.split(":")[1]), reverse=True)

                for index, line in enumerate(leaderboard_data):
                    leaderboard_canvas.create_text(200, 30 + index * 20, text=line.strip(), font=('consolas', 14), fill="white")
        except FileNotFoundError:
            leaderboard_canvas.create_text(200, 150, text="Leaderboard is empty.", font=('consolas', 14), fill="white")

class CarGame():
    def __init__(self, master,  score=0, player_coords=None):
        self.master = master
        self.leaderboard_canvas = None
        
        self.score = score

        
        self.old_lanes = set()
    

        self.rd = Canvas(self.master, width=700, height=720, bg='gray18')
        self.rd.pack()

        # Road
        self.rd.create_line(5, 0, 5, 720, fill='white', width=4)
        self.rd.create_line(175, 0, 175, 720, fill='white', width=4, dash=(50, 30))
        self.rd.create_line(350, 0, 350, 720, fill='white', width=4, dash=(50, 30))
        self.rd.create_line(525, 0, 525, 720, fill='white',  width=4, dash=(50, 30))
        self.rd.create_line(700, 0, 700, 720, fill='white', width=4)

        # Create a player car
        if player_coords is None:
            player_coords = [630, 600, 690, 670]
        self.car = self.rd.create_rectangle(*player_coords, fill='red')
        
        # Create a coin
        self.coin = self.rd.create_oval(0, 0, 0, 0, fill='orange')

        # Score display
        self.score_background = self.rd.create_rectangle(0, 0, 155, 40, fill='black')
        self.score_display = self.rd.create_text(10, 10, anchor=NW, font=('consolas', 20), text=f"Score: {self.score}", fill="red")
      

        self.rd.update()


        #Initialize player keys
        self.left_key = '<Left>'
        self.right_key = '<Right>'
        self.up_key = '<Up>'
        self.down_key = '<Down>'


        # Initialize cheats
        self.invincible = False
        self.double_score_cheat_active = False
        self.old_score = 0  

        #Bind player keys
        self.master.bind(self.left_key, self.move_left)
        self.master.bind(self.right_key, self.move_right)
        self.master.bind(self.up_key, self.move_up)
        self.master.bind(self.down_key, self.move_down)


        # Bind keys for cheats
        self.master.bind('i', self.toggle_invincibility)
        self.master.bind('c', self.activate_double_score_cheat)

        # Bind the boss key event
        self.master.bind('b', self.boss_key)

        # Bind escape key to stop the game
        self.master.bind('<Escape>', self.stop_game)
        
        #Check NPC car movement
        self.move_npc_cars_flag = True

        # Start moving the NPC cars
        self.move_npc_cars()

        

        # Show the coin
        self.show_coin()
    
    def load_saved_keys(self, left_key, right_key, up_key, down_key):
        
        # Unbind default keys
        self.master.unbind(self.left_key)
        self.master.unbind(self.right_key)
        self.master.unbind(self.up_key)
        self.master.unbind(self.down_key)

        # Set new key bindings
        self.left_key = left_key
        self.right_key = right_key
        self.up_key = up_key
        self.down_key = down_key

        # Bind the new keys
        self.master.bind(self.left_key, self.move_left)
        self.master.bind(self.right_key, self.move_right)
        self.master.bind(self.up_key, self.move_up)
        self.master.bind(self.down_key, self.move_down)

        self.move_npc_cars()
    



    def run_game(self):
        self.master.mainloop()
    
    
    def load_data(self, score, player_coords):
        # Set the initial score
        self.score = score

        # Set the player's initial position
        self.rd.coords(self.car, *player_coords)


        # Update the score display
        self.rd.itemconfig(self.score_display, text=f"Score: {self.score}")

        # Start moving the NPC cars
        self.move_npc_cars()

    def stop_game(self, event):
        # Create pause menu
        self.pause_menu = Frame(self.master, width=300, height=320)
        self.pause_menu.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Add buttons to the frame
        resume_button = Button(self.pause_menu, text="Resume", command=self.resume_game)
        save_button = Button(self.pause_menu, text="Save", command=self.save_game)
        menu_button = Button(self.pause_menu, text="Main Menu", command=self.menu)

        # Place buttons in the frame
        resume_button.grid(row=0, column=0, pady=10)
        save_button.grid(row=1, column=0, pady=10)
        menu_button.grid(row=2, column=0, pady=10)

        # Unbind arrow keys
        self.master.unbind(self.left_key)
        self.master.unbind(self.right_key)
        self.master.unbind(self.up_key)
        self.master.unbind(self.down_key)

        # Stop moving NPC cars
        self.move_npc_cars_flag = False

    def resume_game(self):

        #Destroy pause menu

        self.pause_menu.destroy()
        
        self.move_npc_cars_flag = True

         # Bind arrow keys to move the player car
        self.master.bind(self.left_key, self.move_left)
        self.master.bind(self.right_key, self.move_right)
        self.master.bind(self.up_key, self.move_up)
        self.master.bind(self.down_key, self.move_down)

    def save_game(self):
        # Save the game state and score to a file
        with open('savedGame.txt', 'w') as file:

            # Save player's score
            file.write(f"{self.score}\n")

            # Save player's position
            x1, y1, x2, y2 = self.rd.coords(self.car)
            file.write(f"{x1},{y1},{x2},{y2}\n")

        # Inform the player that the game has been saved
        print("Game saved!")
    
    def menu(self):
         # Destroy existing canvas
        self.rd.destroy()

        # Create a new MainMenu instance
        main_menu = MainMenu(self.master)
        main_menu()

    def create_random_car(self, height=60, fill='blue'):
        new_lanes = []

        for number in [60, 225, 415, 575]:
            if number not in self.old_lanes:
                new_lanes.append(number)

        if not new_lanes:
            return None  # No available lanes

        x = random.choice(new_lanes)
        self.old_lanes.add(x)

        y1 = -height  # Start above the canvas
        y2 = y1 + height
        npc_car = self.rd.create_rectangle(x, y1, x + 60, y2, fill=fill)

        # Generate a random speed for the NPC car
        speed = random.randint(20, 50)

        return npc_car, speed


    def move_left(self, event):
        x1, y1, x2, y2 = self.rd.coords(self.car)
        if x1 - 20 > 9:
            self.rd.move(self.car, -40, 0)
        self.check_coin_collision()

    def move_right(self, event):
        x1, y1, x2, y2 = self.rd.coords(self.car)
        if x2 + 20 < 690:
            self.rd.move(self.car, 40, 0)
        self.check_coin_collision()

    def move_up(self, event):
        x1, y1, x2, y2 = self.rd.coords(self.car)
        if y1 > 10:
            self.rd.move(self.car, 0, -40)
        self.check_coin_collision()

    def move_down(self, event):
        x1, y1, x2, y2 = self.rd.coords(self.car)
        if y2 < 710:
            self.rd.move(self.car, 0, 40)
        self.check_coin_collision()
    
    def move_npc_cars(self):
        npc_car, speed = self.create_random_car(fill='blue')
        self.move_npc_car(npc_car, speed)
        self.master.after(1000, self.move_npc_cars)  # Schedule the next NPC car after 1000 milliseconds
    
    def move_npc_car(self, npc_car, speed):

        #Check if the is game paused

        if self.move_npc_cars_flag == False:
            speed = 0
        else:
            speed = random.randint(20, 50)

        if npc_car:
            x1, y1, x2, y2 = self.rd.coords(npc_car)

            # Check for collision with the player car
            if self.check_collision(x1, y1, x2, y2):
                self.game_over()
            
            if y2 < 720:
                self.rd.move(npc_car, 0, speed)
                self.rd.update()
                self.master.after(100, lambda: self.move_npc_car(npc_car, speed))
            else:
                self.old_lanes.remove(x1)
                self.rd.delete(npc_car)
                npc_car, speed = self.create_random_car(fill='blue')
                self.move_npc_car(npc_car, speed)
                if y1 >= 720:  # Reset lanes wh
                    self.old_lanes = set()


    def toggle_invincibility(self, event):
        # Toggle invincibility flag when 'I' key is pressed
        self.invincible = not self.invincible

    def check_collision(self, x1, y1, x2, y2):
        # Get player car coordinates
        player_x1, player_y1, player_x2, player_y2 = self.rd.coords(self.car)

        # Check for collision only if not invincible
        if not self.invincible:
            if (
                player_x1 < x2 and
                player_x2 > x1 and
                player_y1 < y2 and
                player_y2 > y1
            ):
                return True
        return False
    
    def activate_double_score_cheat(self, event):
        # Toggle the double score cheat when 'Shift' and 'C' keys are pressed
        if event.keysym == 'c':
            self.double_score_cheat_active = not self.double_score_cheat_active
            if self.double_score_cheat_active:
                self.old_score = self.score  # Save the current score

    def check_coin_collision(self):
         # Check for collision with the coin
        x1, y1, x2, y2 = self.rd.coords(self.car)
        coin_x1, coin_y1, coin_x2, coin_y2 = self.rd.coords(self.coin)

        if (
            x1 < coin_x2 and
            x2 > coin_x1 and
            y1 < coin_y2 and
            y2 > coin_y1
        ):
            # Apply the double score cheat if active
            if self.double_score_cheat_active:
                self.score += 1+(self.score - self.old_score)  # Add the difference in scores
                self.score += 10  
                self.old_score = self.score  # Update old_score
            else:
                self.score += 1

            self.rd.itemconfig(self.score_display, text=f"Score: {self.score}")

            # Move the coin to a new random position on the road
            self.show_coin()
    
    def boss_key(self, event):

        # Stop the game
        self.stop_game(event)

        # Hide the main window
        self.master.withdraw()

        boss_window = Toplevel()
        boss_window.title("Visual Studio Code")

        # Load the boss image using Pillow
        boss_image = Image.open("boss.png")
        self.boss_image = ImageTk.PhotoImage(boss_image.resize((1280, 720))) # Resize the image
        boss_canvas = Canvas(boss_window, width=1280, height=720)
        boss_canvas.pack()

        # Display the boss image on the canvas
        boss_canvas.create_image(640, 360, anchor=CENTER, image=self.boss_image)  # Center the image

        # Center the window
        boss_window.update_idletasks()
        width = boss_window.winfo_width()
        height = boss_window.winfo_height()
        x = (boss_window.winfo_screenwidth() - width) // 2
        y = (boss_window.winfo_screenheight() - height) // 2
        boss_window.geometry(f"{width}x{height}+{x}+{y}")

        # Bind a function to close the boss window and show the main window again
        boss_window.bind('<KeyPress-b>', lambda event: self.close_boss_window(event, boss_window))

    def close_boss_window(self, event, boss_window):
        # Unhide the main window
        self.master.deiconify()

        # Close the boss window
        boss_window.destroy()


    def show_coin(self):
        # Calculate the grid size based on the coin size
        grid_size = 30

        # Calculate the maximum valid position
        max_x = 670 - grid_size
        max_y = 720 - grid_size

        # Show the coin at a random position on the road within the canvas bounds
        if max_x >= 15:
            coin_x = random.randint(0, max_x // grid_size) * grid_size
            coin_y = random.randint(0, max_y // grid_size) * grid_size
            self.rd.coords(self.coin, coin_x, coin_y, coin_x + 30, coin_y + 30)

    def game_over(self):
         # Get player's name
        player_name = askstring("Input", "Game Over please Enter your name:")

        # Destroy existing canvas
        self.rd.destroy()

        # Create a new canvas for Game Over text and buttons
        self.game_over_canvas = Canvas(self.master, width=700, height=720, bg='black')
        self.game_over_canvas.pack()

        self.game_over_canvas.create_text(700/2, 720/2, font=('consolas', 70), text="GAME OVER", fill="red")
        self.game_over_canvas.create_text(700/2, 720/2+75, font=('consolas', 35), text=f"Your Score: {self.score}", fill="white")
        self.game_over_canvas.create_text(700/2, 720/2+150, font=('consolas', 25), text=f"Player: {player_name}", fill="white")
        # Save the score and player name to a leaderboard file
        with open('leaderboard.txt', 'a') as file:
            file.write(f"{player_name}: {self.score}\n")

        style = Style()
        style.configure('TButton', font=('calibri', 20, 'bold'), borderwidth='4')
        style.map('TButton', foreground=[('active', '!disabled', 'green')])

        # Create buttons in the game over screen

        main_menu_button = Button(self.master, text="Main Menu", style='TButton', command=self.main_menu)
        restart_button = Button(self.master, text="Restart", style='TButton', command=self.restart_game)
        leaderboard_button = Button(self.master, text="Leaderboard", style='TButton', command=self.show_leaderboard)

        # Place buttons in the center
        main_menu_button.place(relx=0.5, rely=0.8, anchor=CENTER)
        restart_button.place(relx=0.4, rely=0.9, anchor=CENTER)
        leaderboard_button.place(relx=0.6, rely=0.9, anchor=CENTER)

    def extract_score(self, line):
        return int(line.split(":")[1])

    def show_leaderboard(self):
        # Read, sort, and display the leaderboard from the file
        leaderboard_window = Toplevel(self.master)
        leaderboard_window.title("Leaderboard")

        self.leaderboard_canvas = Canvas(leaderboard_window, width=400, height=300, bg='black')
        self.leaderboard_canvas.pack()

        try:
            with open('leaderboard.txt', 'r') as file:
                leaderboard_data = file.readlines()

                # Sort the leaderboard data based on scores
                leaderboard_data.sort(key=self.extract_score, reverse=True)

                # Display sorted leaderboard text on the canvas
                for index, line in enumerate(leaderboard_data):
                    self.leaderboard_canvas.create_text(200, 30 + index * 20, text=line.strip(), font=('consolas', 14),
                                                        fill="white")
        except FileNotFoundError:
            self.leaderboard_canvas.create_text(200, 150, text="Leaderboard is empty.", font=('consolas', 14),
                                                fill="white")
    def restart_game(self):
        # Destroy existing canvas
        self.game_over_canvas.destroy()

        # Create a new CarGame instance
        new_game = CarGame(self.master)

        # Run the game
        new_game.run_game()
    
    def main_menu(self):
        self.game_over_canvas.destroy()

         # Create a new MainMenu instance
        main_menu = MainMenu(self.master)
        main_menu()

def configure_window(window):
    window.geometry("1280x720")
    window.configure(background='#F8F8FF')
    window.title("Wrong Lane!")
    window.resizable(False, False)

    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

window = Tk()
configure_window(window)
main_menu = MainMenu(window)
window.mainloop() 