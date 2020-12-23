import arcade
from game_map import load_maps
from game_view import GameView
from draw_bar import draw_bar

class LoadingView(arcade.View):
    def __init__(self):
        super().__init__()
        self.started = False
        arcade.set_background_color(arcade.color.ALMOND)
        self.progress = 0

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Loading...",
                         self.window.width / 2,
                         self.window.height / 2,
                         arcade.color.ALLOY_ORANGE,
                         44,
                         anchor_x="center", anchor_y="center", align="center")
        self.started = True
        draw_bar(current_amount=self.progress,
                 max_amount=100,
                 center_x=self.window.width / 2,
                 center_y=20,
                 width=self.window.width,
                 height=10,
                 color_a=arcade.color.BLACK,
                 color_b=arcade.color.WHITE)

    def setup(self):
        pass

    def on_update(self, delta_time: float):
        # Dictionary to hold all our maps
        if self.started:
            done, self.progress, self.map_list = load_maps()
            if done:
                start_view = GameView(self.map_list)
                start_view.setup()
                self.window.show_view(start_view)