import matplotlib.pyplot as plt
import numpy as np
from soccerdata.fbref import FBref
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.patches import RegularPolygon
from matplotlib.spines import Spine
from matplotlib.path import Path
from matplotlib.transforms import Affine2D

def radar_factory(num_vars, frame='polygon'):
    """Create a radar chart with `num_vars` axes."""
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):
        name = 'radar'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')

        def plot(self, *args, **kwargs):
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels, fontsize=12, color='black')

        def _gen_axes_patch(self):
            if frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars, radius=.5, edgecolor="black")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def draw(self, renderer):
            super().draw(renderer)

        def _gen_axes_spines(self):
            if frame == 'polygon':
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5) + self.transAxes)
                spine.set_edgecolor('black')
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta

def fetch_player_data(player_name, leagues, seasons):
    """
    Fetches soccer player data using the FBref class.

    Args:
        player_name (str): Name of the player to search.
        leagues (list): List of leagues to include.
        seasons (list): List of seasons to include.

    Returns:
        dict: Player stats including progressive carries, assists per 90, successful take-ons per 90,
              shot creating actions per 90, expected assists per 90, and expected goals per 90.
    """
    fbref = FBref(leagues=leagues, seasons=seasons)

    # Fetch different stat types
    standard_data = fbref.read_player_season_stats(stat_type="standard")
    passing_data = fbref.read_player_season_stats(stat_type="passing")
    gca_data = fbref.read_player_season_stats(stat_type="goal_shot_creation")
    possession_data = fbref.read_player_season_stats(stat_type="possession")

    # Print all columns
    print("Standard Data Columns:", standard_data.columns)
    print("Passing Data Columns:", passing_data.columns)
    print("GCA Data Columns:", gca_data.columns)
    print("Possession Data Columns:", possession_data.columns)

    # Filter player stats based on the player's name
    player_standard = standard_data[standard_data.index.get_level_values("player") == player_name]
    player_passing = passing_data[passing_data.index.get_level_values("player") == player_name]
    player_gca = gca_data[gca_data.index.get_level_values("player") == player_name]
    player_possession = possession_data[possession_data.index.get_level_values("player") == player_name]

    if player_standard.empty:
        raise ValueError(f"No data found for player {player_name}")

    # Extract relevant stats
    try:
        stats = {
            "Progressive Carries per 90": player_possession["Carries", "PrgC"].values[0] / player_standard["Playing Time", "90s"].values[0],
            "Carries into penalty Aeria per 90": player_possession["Carries", "CPA"].values[0] / player_standard["Playing Time", "90s"].values[0],
            "Successful Take-ons per 90": player_possession["Take-Ons", "Succ"].values[0] / player_standard["Playing Time", "90s"].values[0],
            "Shot Creating Actions per 90": player_gca["SCA", "SCA90"].values[0],
            "Expected Assists per 90": player_standard["Expected", "xAG"].values[0],
            "Expected Goals per 90": player_standard["Expected", "xG"].values[0],
            "Key Passes per 90": player_passing["KP", ""].values[0]/ player_standard["Playing Time", "90s"].values[0],
        }
    except KeyError as e:
        print(f"KeyError: {e}. Please check column names in the data.")
        raise

    return stats

def plot_spider_graph(player1_name, player1_stats, player2_name, player2_stats, player3_name, player3_stats, player4_name, player4_stats, player5_name, player5_stats, player6_name, player6_stats):
    """
    Plots a radar chart comparing players.

    Args:
        player1_name (str): Name of the first player.
        player1_stats (dict): Stats of the first player.
        player2_name (str): Name of the second player.
        player2_stats (dict): Stats of the second player.
        player3_name (str): Name of the third player.
        player3_stats (dict): Stats of the third player.
        player4_name (str): Name of the fourth player.
        player4_stats (dict): Stats of the fourth player.
        player5_name (str): Name of the fifth player.
        player5_stats (dict): Stats of the fifth player.
        player6_name (str): Name of the sixth player.
        player6_stats (dict): Stats of the sixth player.
    """
    categories = list(player1_stats.keys())
    num_vars = len(categories)
    theta = radar_factory(num_vars)

    # Prepare data
    player1_values = list(player1_stats.values())
    player2_values = list(player2_stats.values())
    player3_values = list(player3_stats.values())
    player4_values = list(player4_stats.values())
    player5_values = list(player5_stats.values())
    player6_values = list(player6_stats.values())

    # Plot setup
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='radar'))

    ax.plot(theta, player1_values, color="blue", linewidth=2, label=player1_name)
    ax.fill(theta, player1_values, color="blue", alpha=0.15)

    ax.plot(theta, player2_values, color="red", linewidth=2, label=player2_name)
    ax.fill(theta, player2_values, color="red", alpha=0.15)

    ax.plot(theta, player3_values, color="green", linewidth=2, label=player3_name)
    ax.fill(theta, player3_values, color="green", alpha=0.15)

    ax.plot(theta, player4_values, color="purple", linewidth=2, label=player4_name)
    ax.fill(theta, player4_values, color="purple", alpha=0.15)

    ax.plot(theta, player5_values, color="orange", linewidth=2, label=player5_name)
    ax.fill(theta, player5_values, color="orange", alpha=0.15)

    ax.plot(theta, player6_values, color="yellow", linewidth=2, label=player6_name)
    ax.fill(theta, player6_values, color="yellow", alpha=0.15)

    ax.set_yticklabels([])

    ax.set_varlabels(categories)

    # Add legend
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2)

    # Show the plot
    plt.title(f"Comparison of {player1_name}, {player2_name}, {player4_name}, {player3_name}, {player5_name}, and {player6_name}", size=15, color="black", y=1.1)
    plt.show()

def main():
    print("Soccer Player Comparison")
    player1_name = "Marcus Rashford"
    player2_name = "Alejandro Garnacho"
    player3_name = "Amad Diallo"
    player4_name = "Antony"
    player5_name = "Rasmus Højlund"
    player6_name = "Joshua Zirkzee"
    leagues = ["Big 5 European Leagues Combined"]
    seasons = ["2024-2025"]

    try:
        player1_stats = fetch_player_data(player1_name, leagues, seasons)
        player2_stats = fetch_player_data(player2_name, leagues, seasons)
        player3_stats = fetch_player_data(player3_name, leagues, seasons)
        player4_stats = fetch_player_data(player4_name, leagues, seasons)
        player5_stats = fetch_player_data(player5_name, leagues, seasons)
        player6_stats = fetch_player_data(player6_name, leagues, seasons)

        print(f"{player1_name} Stats: {player1_stats}")
        print(f"{player2_name} Stats: {player2_stats}")
        print(f"{player3_name} Stats: {player3_stats}")
        print(f"{player4_name} Stats: {player4_stats}")
        print(f"{player5_name} Stats: {player5_stats}")
        print(f"{player6_name} Stats: {player6_stats}")

        # Plot radar chart with six players
        plot_spider_graph(player1_name, player1_stats, player2_name, player2_stats, player3_name, player3_stats, player4_name, player4_stats, player5_name, player5_stats, player6_name, player6_stats)
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
