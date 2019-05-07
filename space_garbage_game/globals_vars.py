coroutines = []
obstacles = []
obstacles_in_last_collisions = []
spaceship_frames_coroutines = []

TIC_TIMEOUT = 0.1
STARS_SYMBOLS = '+*.:'
BORDER_SIZE = 2
FRAME_FOLDER = r'frames'
GARBAGE_FRAMES = [r'duck.txt', r'hubble.txt', r'lamp.txt', r'trash_large.txt',
                  r'trash_small.txt', r'trash_xl.txt']
SPACESHIP_FRAMES = [r'rocket_frame_1.txt', r'rocket_frame_2.txt']


PHRASES_DICT = {1957: "First Sputnik",
                1961: "Gagarin flew!",
                1969: "Armstrong got on the moon!",
                1971: "First orbital space station Salute-1",
                1981: "Flight of the Shuttle Columbia",
                1998: 'ISS start building',
                2011: 'Messenger launch to Mercury',
                2020: "Yamato cannon is charged! Shoot the garbage!"}

EXPLOSION_FRAMES = [r'explode1.txt', r'explode2.txt', r'explode3.txt',
                    r'explode4.txt']


# EXPLOSION_FRAMES = [
#     """\
#            (_)
#        (  (   (  (
#       () (  (  )
#         ( )  ()
#     """,
#     """\
#            (_)
#        (  (   (
#          (  (  )
#           )  (
#     """,
#     """\
#             (
#           (   (
#          (     (
#           )  (
#     """,
#     """\
#             (
#               (
#             (
#     """,
# ]