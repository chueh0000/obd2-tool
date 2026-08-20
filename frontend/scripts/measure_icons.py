from PIL import Image

img = Image.open("/Users/howardchueh/.gemini/antigravity/brain/25beaf5f-3080-4cd7-b9ad-19c4cbc59c83/media__1786967675915.png").convert("L")
w, h = img.size
w_quarter = w // 4
pixels = img.load()

for i, name in enumerate(["Fuel", "Battery", "Coolant", "Oil"]):
    xmin, xmax = w, -1
    ymin, ymax = h, -1
    area = 0
    for y in range(int(h*0.6), h):
        for x in range(i*w_quarter, (i+1)*w_quarter):
            if pixels[x, y] > 200: # threshold
                if x < xmin: xmin = x
                if x > xmax: xmax = x
                if y < ymin: ymin = y
                if y > ymax: ymax = y
                area += 1
    
    if area > 0:
        bw = xmax - xmin + 1
        bh = ymax - ymin + 1
        print(f"{name}: width={bw}, height={bh}, area={area}, aspect={bw/bh:.2f}")
    else:
        print(f"{name}: not found")
