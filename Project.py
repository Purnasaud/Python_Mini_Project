from tkinter import *
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import geopandas
import matplotlib.pyplot as plt
import math
import random


root = Tk(className='SimpleGIS')

fig, ax = plt.subplots(figsize=(10, 5))


def haversine_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def viewing_map(filelocation):
    global df
    df = geopandas.read_file(filelocation)
    open.config(text="Add Data")
    savegeojson.config(state='normal')
    saveshp.config(state='normal')
    measure.config(state='normal')
    attrib.config(state='normal')
    crsinf.config(state='normal')
    r = lambda: random.randint(0, 255)
    colors = ('#%02X%02X%02X' % (r(), r(), r()))
    df.plot(ax=ax, color=colors)
    plt.title('Map')
    plt.subplots_adjust(left=0.04, bottom=0.06, right=0.99, top=0.95, wspace=0.2, hspace=0.2)
    plt.show()


def totaldistance(coords):
    total_len = 0
    _temp = coords[0]
    for every in coords:
        if df.crs == 'epsg:3395':
            total_len = total_len + math.sqrt((every[0] - _temp[0]) ** 2 + (every[1] - _temp[1]) ** 2)
        elif df.crs == 'epsg:4326':
            total_len = total_len + haversine_distance(every, _temp)
        _temp = every
    return total_len


def segmentdistance(coords):
    seg_len = 0
    last_two = coords[-2:]
    seg_len = totaldistance(last_two)
    return seg_len


coords = []


def onclick(event):
    ix, iy = event.xdata, event.ydata
    global coords
    coords.append((ix, iy))
    if len(coords) >= 2:
        total_dist = totaldistance(coords)
        segment_dist = segmentdistance(coords)
        tkMessageBox.showinfo("Distance (Km)",
                              "Total Length = %s \n Segment Length = %s" % (str(total_dist), str(segment_dist)))
        fig.canvas.mpl_disconnect(cid)
        coords = []


def measuredistance():
    global cid
    cid = fig.canvas.mpl_connect('button_press_event', onclick)


def opening_data():
    filename = tkFileDialog.askopenfilename(initialdir=".", title="Select file",
                                            filetypes=(("shapefiles", "*.shp"), ("all files", "*.*")))
    if filename is None:
        return
    viewiyng_map(filename)


def show_projection_info():
    tkMessageBox.showinfo("CRS info", df.crs)


def file_save():
    f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".geojson")
    if f is None:
        return
    f.write(df.to_json())
    f.close()


def save_shapefile():
    ds = geopandas.GeoDataFrame(df, geometry='geometry')
    ds.crs = "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
    fi = tkFileDialog.askdirectory()
    if fi is None:
        return
    fi = fi + "/Export_output.shp"
    df.to_file(fi, driver='ESRI Shapefile')


def show_about():
    tkMessageBox.showinfo("About this App", "This was made as a python miniproject by \n Binabh Devkota")


def show_arrtibtable():
    table = Toplevel()
    table.geometry('800x800')
    table.wm_title("Attribute Table")
    l = Text(table, height=800, width=800)
    l.insert(END, df.head(n=len(df)))
    l.config(state=DISABLED)
    scrollvertical = Scrollbar(table, orient=VERTICAL)
    scrollhorizontal = Scrollbar(table, orient=HORIZONTAL)
    scrollvertical.pack(side=RIGHT, fill=Y)
    scrollhorizontal.pack(side=BOTTOM, fill=X)
    l.pack()
    scrollvertical.config(command=l.yview)
    scrollhorizontal.config(command=l.xview)
    l.config(yscrollcommand=scrollvertical.set)
    l.config(xscrollcommand=scrollhorizontal.set)


open = Button(root, text="Open Data", command=opening_data)
open.pack(side=LEFT)
measure = Button(root, text="Measure Tool", command=measuredistance, state=DISABLED)
measure.pack(side=LEFT)
savegeojson = Button(root, text="Save as GeoJson", command=file_save, state=DISABLED)
savegeojson.pack(side=LEFT)
saveshp = Button(root, text="Save as Shapefile", command=save_shapefile, state=DISABLED)
saveshp.pack(side=LEFT)
attrib = Button(root, text="Show attribute data", command=show_arrtibtable, state=DISABLED)
attrib.pack(side=LEFT)
crsinf = Button(root, text="Show Projection info", command=show_projection_info, state=DISABLED)
crsinf.pack(side=LEFT)
Button(root, text="About App", command=show_about).pack(side=LEFT)
root.mainloop()