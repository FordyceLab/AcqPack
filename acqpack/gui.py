import time

import cv2
import matplotlib.pyplot as plt
import numpy as np
from IPython import display
from ipywidgets import widgets


# --------------------------------------------------------------------  
# IMSHOW -------------------------------------------------------------
def imshow(img, name='Image', mode='cv2'):
    if mode == 'cv2':
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(name, 500, 500)
        cv2.setWindowProperty(name, cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
        cv2.imshow(name, img)
        k = cv2.waitKey(30)
    else:
        plt.imshow(img, cmap='gray')
        plt.show()


# --------------------------------------------------------------------  
# SNAP ---------------------------------------------------------------
def snap(core, mode='mpl'):
    def on_snap_mpl(b):
        core.snapImage()
        img = core.getImage()
        plt.imshow(img, cmap='gray')
        plt.show()

    def on_snap_cv2(b):
        cv2.destroyWindow('Snap')
        cv2.namedWindow('Snap', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Snap', 500, 500)
        cv2.setWindowProperty('Snap', cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
        core.snapImage()
        time.sleep(.1)
        img = core.getImage()
        cv2.imshow('Snap', img)
        k = cv2.waitKey(30)

    def on_close_cv2(b):
        cv2.destroyWindow('Snap')

    snap = widgets.Button(description='Snap')

    if mode == 'cv2':
        snap.on_click(on_snap_cv2)
        close = widgets.Button(description='Close')
        close.on_click(on_close_cv2)
        display.display(widgets.HBox([snap, close]))
    else:  # mode=='mpl'
        snap.on_click(on_snap_mpl)
        display.display(snap)


# --------------------------------------------------------------------
# VIDEO ------------------------------------------------------
def video(core, loop_pause=0.15):
    # video with button (CV2)
    live = widgets.Button(description='Live')
    close = widgets.Button(description='Close')
    display.display(widgets.HBox([live, close]))

    def on_live(b):
        display.clear_output(wait=True)
        print 'LIVE'
        core.startContinuousSequenceAcquisition(1000)  # time overridden by exposure
        time.sleep(.2)
        cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Video', cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
        cv2.resizeWindow('Video', 500, 500)
        img = np.zeros((500, 500))
        print 'To stop, click window + press ESC'
        while 1:
            time.sleep(loop_pause)
            if core.getRemainingImageCount() > 0:
                img = core.getLastImage()
            cv2.imshow('Video', img)
            k = cv2.waitKey(30)
            if k == 27:  # ESC key; may need 255 mask?
                break
        print 'STOPPED'
        core.stopSequenceAcquisition()

    def on_close(b):
        if core.isSequenceRunning():
            core.stopSequenceAcquisition()
        cv2.destroyWindow('Video')

    live.on_click(on_live)
    close.on_click(on_close)

    # video with button (CV2)
    # serial snap image

    # live = widgets.Button(description='Live')
    # close = widgets.Button(description='Close')
    # display.display(widgets.HBox([live, close]))

    # def on_live_clicked(b):
    #     display.clear_output(wait=True)
    #     print 'LIVE'
    #     cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
    #     cv2.setWindowProperty('Video', cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
    #     cv2.resizeWindow('Video', 500,500)
    #     img = np.zeros((500,500))
    #     print 'To stop, click window + press ESC'
    #     while(1):
    #         core.snapImage()
    #         time.sleep(.05)
    #         img = core.getImage()
    #         cv2.imshow('Video',img)
    #         k = cv2.waitKey(30)
    #         if k==27: # ESC key; may need 255 mask?
    #             break
    #     print 'STOPPED'

    # def on_close_clicked(b):
    #     if core.isSequenceRunning():
    #         core.stopSequenceAcquisition()
    #     cv2.destroyWindow('Video')

    # live.on_click(on_live_clicked)
    # close.on_click(on_close_clicked)


# --------------------------------------------------------------------  
# GRID ------------------------------------------------------
def grid(core, loop_pause=0.15):
    # video with button (CV2)

    def on_live(b):
        display.clear_output(wait=True)
        print 'LIVE'
        core.startContinuousSequenceAcquisition(1000)  # time overridden by exposure
        time.sleep(.2)
        cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Video', cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
        cv2.resizeWindow('Video', 500, 500)
        img = np.zeros((500, 500))
        print 'To stop, click window + press ESC'
        while 1:
            time.sleep(loop_pause)
            if core.getRemainingImageCount() > 0:
                img = core.getLastImage()
            cv2.imshow('Video', img)
            k = cv2.waitKey(30)
            if k == 27:  # ESC key; may need 255 mask?
                break
        print 'STOPPED'
        core.stopSequenceAcquisition()

    def on_close(b):
        if core.isSequenceRunning():
            core.stopSequenceAcquisition()
        cv2.destroyWindow('Video')

    def on_corner(b):
        pos = core.get_xy()
        b.owner.value = pos
        print pos

    live = widgets.Button(description='Live')
    close = widgets.Button(description='Close')

    c1 = widgets.Button(description='Corner 1')
    c2 = widgets.Button(description='Corner 2')
    file = widgets.Text()
    save = widgets.Text()

    live.on_click(on_live)
    close.on_click(on_close)

    c1.on_click(on_corner)
    c2.on_click(on_corner)

    # calculate: c1.value - c2.value
    save.on_click(icon='floppy-o')

    display.display(widgets.HBox([live, close]))


# --------------------------------------------------------------------
# MANIFOLD -----------------------------------------------------------
def manifold_control(manifold):
    def on_clicked(b):
        if b.new:  # b.new == True
            manifold.depressurize(b.owner.valve)
        else:  # b.new == False
            manifold.pressurize(b.owner.valve)

    def sync(b):
        for button in button_list:
            button.value = manifold.read_valve(button.valve)

    button_list = []
    for i in range(48):
        style = 'info'
        desc = '{} {}'.format(i, manifold.valvemap['name'][i])

        button_list.append(
            widgets.ToggleButton(
                valve=i,
                description=desc,
                value=manifold.read_valve(i),
                button_style=style  # 'success', 'info', 'warning', 'danger' or ''
            ))

    for button in button_list:
        button.observe(on_clicked)

    bank_list = []
    for i in range(0, 48, 8):
        bank_list.append(
            widgets.VBox(button_list[i:i + 8][::-1])
        )

    sync_button = widgets.Button(icon='fa-retweet', button_style='success', layout=widgets.Layout(width='40px'))
    sync_button.on_click(sync)
    display.display(widgets.HBox(bank_list + [sync_button]))
    display.display(widgets.Label('Dark = De-Pressurized', layout=widgets.Layout(width='300px')))


# --------------------------------------------------------------------  
# STAGE CONTROL ------------------------------------------------------
def stage_control(xy, z):
    # icons are from "font-awesome"
    x_minus = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon='fa-arrow-left',
        width='50px')

    def xminus(b):
        xy.move_relative_xy(-xy_slider.value, 0)
        display.clear_output()
        print(xy.where_xy())

    x_minus.on_click(xminus)

    x_plus = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon='fa-arrow-right',
        width='50px')

    def xplus(b):
        xy.r_xy(xy_slider.value, 0)
        display.clear_output()
        print(xy.where_xy())

    x_plus.on_click(xplus)

    y_minus = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon='fa-arrow-up',
        width='50px')

    def yminus(b):
        xy.r_xy(0, -xy_slider.value)
        display.clear_output()
        print(xy.where_xy())

    y_minus.on_click(yminus)

    y_plus = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon='fa-arrow-down',
        width='50px')

    def yplus(b):
        xy.r_xy(0, xy_slider.value)
        display.clear_output()
        print(xy.where_xy())

    y_plus.on_click(yplus)

    xy_home = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon='fa-home',
        width='50px')

    def xyhome(b):
        z.home()
        xy.goto_xy(0, 0)
        display.clear_output()
        print(xy.where_xy())

    xy_home.on_click(xyhome)

    xy_slider = widgets.FloatSlider(description='[mm]', min=.05, max=10, step=.05, orientation='vertical',
                                    height='150px')

    def xystep(change):
        xy_step = change['new']

    xy_slider.observe(xystep, names='value')

    xy_cluster = widgets.HBox(
        [xy_slider, widgets.VBox([widgets.HBox([x_minus, x_plus, xy_home]), widgets.HBox([y_minus, y_plus])])])

    z_minus = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon='fa-arrow-up')

    def zminus(b):
        z.move_relative(-z_slider.value)
        display.clear_output()
        print(z.where())

    z_minus.on_click(zminus)

    z_plus = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon='fa-arrow-down')

    def zplus(b):
        z.move_relative(z_slider.value)
        display.clear_output()
        print(z.where())

    z_plus.on_click(zplus)

    z_home = widgets.Button(
        description='',
        disabled=False,
        button_style='primary',
        icon='fa-home',
        width='50px')

    def zhome(b):
        z.home()
        display.clear_output()
        print(z.where())

    z_home.on_click(zhome)

    z_slider = widgets.FloatSlider(description='[mm]', min=.05, max=10, step=.05, orientation='vertical',
                                   height='150px')

    def zstep(change):
        z_step = change['new']

    z_slider.observe(zstep, names='value')

    z_cluster = widgets.VBox([widgets.HBox([z_slider, widgets.VBox([z_minus, z_plus]), z_home])])

    x_pos = widgets.Text(
        value='0',
        placeholder='Type something',
        description='X:',
        disabled=False,
        width='150px')

    def xpos(sender):
        xcurr, ycurr = xy.where_xy()
        xy.goto_xy(sender.value, ycurr)

    x_pos.on_submit(xpos)

    y_pos = widgets.Text(
        value='0',
        placeholder='Type something',
        description='Y:',
        disabled=False,
        width='150px')

    def ypos(sender):
        xcurr, ycurr = xy.where_xy()
        xy.goto_xy(xcurr, sender.value)

    y_pos.on_submit(ypos)

    z_pos = widgets.Text(
        value='0',
        placeholder='Type something',
        description='z:',
        disabled=False,
        width='150px')

    def zpos(sender):
        z.goto(float(sender.value))

    z_pos.on_submit(zpos)

    line = widgets.Label(value="$---------------------------------------$", disabled=False)

    return widgets.VBox([widgets.HBox([x_pos, y_pos, z_pos]), line, widgets.HBox([xy_cluster, z_cluster])])


# --------------------------------------------------------------------
# STAGE CONTROL2------------------------------------------------------
def stage_control2(xy, z):
    # icons are from "font-awesome"

    # xy ------------------------------------------------------------
    x_minus = widgets.Button(
        ax='x',
        sign=-1,
        button_style='primary',
        icon='fa-arrow-left',
        width='50px')

    x_plus = widgets.Button(
        ax='x',
        sign=1,
        button_style='primary',
        icon='fa-arrow-right',
        width='50px')

    y_minus = widgets.Button(
        ax='y',
        sign=-1,
        button_style='primary',
        icon='fa-arrow-up',
        width='50px')

    y_plus = widgets.Button(
        ax='y',
        sign=1,
        button_style='primary',
        icon='fa-arrow-down',
        width='50px')

    xy_home = widgets.Button(
        ax='xy',
        button_style='primary',
        icon='fa-home',
        width='50px')

    xy_slider = widgets.FloatSlider(description='[mm]', min=.05, max=10, step=.05, orientation='vertical',
                                    height='150px')
    # xy_slider.observe(step, names='value')

    xy_cluster = widgets.HBox(
        [xy_slider, widgets.VBox([widgets.HBox([x_minus, x_plus, xy_home]), widgets.HBox([y_minus, y_plus])])])

    # z ------------------------------------------------------------
    z_minus = widgets.Button(
        ax='z',
        sign=-1,
        button_style='primary',
        icon='fa-arrow-up')

    z_plus = widgets.Button(
        ax='z',
        sign=1,
        button_style='primary',
        icon='fa-arrow-down')

    z_home = widgets.Button(
        button_style='primary',
        icon='fa-home',
        width='50px')

    z_slider = widgets.FloatSlider(description='[mm]',
                                   min=.05, max=10,
                                   step=.05,
                                   orientation='vertical',
                                   height='150px')
    # z_slider.observe(zstep, names='value')

    z_cluster = widgets.VBox([widgets.HBox([z_slider, widgets.VBox([z_minus, z_plus]), z_home])])

    # type to move ------------------------------------------------------------
    x_pos = widgets.Text(
        value='0',
        placeholder='enter pos',
        description='X:',
        width='150px')

    y_pos = widgets.Text(
        value='0',
        placeholder='enter pos',
        description='Y:',
        width='150px')

    z_pos = widgets.Text(
        value='0',
        placeholder='enter pos',
        description='z:',
        width='150px')

    # functions ------------------------------------------------------------
    def move(b):
        if b.owner.ax == 'x':
            xy.move_relative_xy(b.owner.sign * xy_slider.value, 0)
        elif b.owner.ax == 'y':
            xy.move_relative_xy(0, b.owner.sign * xy_slider.value)
        elif b.owner.ax == 'z':
            z.move_relative(b.owner.sign * z_slider.value)

        display.clear_output()
        print(xy.where_xy() + z.where())

    for button in [x_minus, x_plus, y_minus, y_plus, z_minus, z_plus]:
        button.on_click(move)

    def home(b):
        if b.owner.ax == 'xy':
            z.home()
            xy.home()
        elif b.owner.ax == 'z':
            z.home()

        display.clear_output()
        print(xy.where_xy() + z.where())

    for button in [xy_home, z_home]:
        button.on_click(home)

    def pos(b):
        if b.owner.ax == 'x':
            x_curr, y_curr = xy.where_xy()
            xy.goto_xy(b.value, y_curr)
        if b.owner.ax == 'y':
            x_curr, y_curr = xy.where_xy()
            xy.goto_xy(x_curr, b.value)
        elif b.owner.ax == 'z':
            z.goto(float(b.value))

        display.clear_output()
        print(xy.where_xy() + z.where())

    for button in [x_pos, y_pos, z_pos]:
        button.on_submit(pos)

    # def step(change):
    #     xy_step = change['new']

    # for slider in [xy_slider, z_slider]:
    #     slider.observe(step, names='value')

    line = widgets.Label(value="$---------------------------------------$")

    return widgets.VBox([widgets.HBox([x_pos, y_pos, z_pos]), line, widgets.HBox([xy_cluster, z_cluster])])
