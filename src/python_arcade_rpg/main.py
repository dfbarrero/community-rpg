"""
Python Arcade Community RPG

An open-source RPG
"""
from collections import OrderedDict
import arcade

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Python Community RPG"
TILE_SCALING = 1.0

MOVEMENT_SPEED = 3

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 300
RIGHT_VIEWPORT_MARGIN = 300
BOTTOM_VIEWPORT_MARGIN = 300
TOP_VIEWPORT_MARGIN = 300


class Character(arcade.Sprite):
    def __init__(self, sheet_name):
        super().__init__()
        self.textures = arcade.load_spritesheet(sheet_name,
                                                sprite_width=32,
                                                sprite_height=32,
                                                columns=3,
                                                count=12)
        self.cur_texture_index = 0
        self.texture = self.textures[self.cur_texture_index]

    def update(self):
        if not self.change_x and not self.change_y:
            return

        # self.center_x += self.change_x
        # self.center_y += self.change_y

        self.cur_texture_index += 1
        if self.change_x > 0:
            if self.cur_texture_index < 6:
                self.cur_texture_index = 6
            elif self.cur_texture_index > 8:
                self.cur_texture_index = 6
        elif self.change_x < 0:
            if self.cur_texture_index < 3:
                self.cur_texture_index = 3
            elif self.cur_texture_index > 5:
                self.cur_texture_index = 3
        elif self.change_y > 0:
            if self.cur_texture_index < 9:
                self.cur_texture_index = 9
            elif self.cur_texture_index > 11:
                self.cur_texture_index = 9
        else:
            if self.cur_texture_index < 0:
                self.cur_texture_index = 0
            elif self.cur_texture_index > 2:
                self.cur_texture_index = 0

        self.texture = self.textures[self.cur_texture_index]


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)

        arcade.set_background_color(arcade.color.AMAZON)

        self.player_sprite = None
        self.player_sprite_list = None

        # Sprite Lists
        self.map_layers = OrderedDict()

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.view_left = 0
        self.view_bottom = 0

        self.physics_engine = None

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """

        # Sprite Lists
        # Name of map file to load
        map_name = "sample_map/samplemap.tmx"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # List of blocking sprites
        self.wall_list = arcade.SpriteList()

        for layer in my_map.layers:

            try:
                print(f"Loading layer: {layer.name}")
                self.map_layers[layer.name] = arcade.tilemap.process_layer(map_object=my_map,
                                                                           layer_name=layer.name,
                                                                           scaling=TILE_SCALING,
                                                                           use_spatial_hash=True)

                # Any layer with '_blocking' in it, will be a wall
                if '_blocking' in layer.name:
                    self.wall_list.extend(self.map_layers[layer.name])

            except Exception as e:
                print(f"Can't load {layer.name} - {e}")

        self.player_sprite = Character("characters/Female/Female 18-4.png")
        self.player_sprite.center_x = 500
        self.player_sprite.center_y = 1000
        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        # Call draw() on all your sprite lists below
        for map_layer_name in self.map_layers:
            self.map_layers[map_layer_name].draw()

        self.player_sprite_list.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        """
        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = MOVEMENT_SPEED

        # Call update to move the sprite
        # If using a physics engine, call update player to rely on physics engine
        # for movement, and call physics engine here.
        self.physics_engine.update()
        self.player_sprite_list.update()

        # --- Manage Scrolling ---

        changed_viewport = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_viewport = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_viewport = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_viewport = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_viewport = True

        if changed_viewport:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player_sprite.destination_point = x, y

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass


def main():
    """ Main method """
    game = MyGame()
    game.center_window()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
