import time, math, os
import numpy as np
import cv2

W, H = 800, 600
FPS = 30
DURATION = 48.0

def clamp01(x): return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)
def smoothstep(a, b, x):
    x = clamp01((x - a) / (b - a))
    return x * x * (3 - 2 * x)

def poly_param(fx, fy, t0, t1, n, cx, cy, sx, sy):
    ts = np.linspace(t0, t1, n, dtype=np.float32)
    xs = fx(ts) * sx + cx
    ys = fy(ts) * sy + cy
    return np.round(np.stack([xs, ys], 1)).astype(np.int32).reshape((-1, 1, 2))

def hsv_to_bgr(h, s, v):
    hsv = np.uint8([[[h % 180, np.clip(s, 0, 255), np.clip(v, 0, 255)]]])
    return tuple(int(x) for x in cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0])

def post_vignette(img, strength=0.7):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx - W*0.5) / (W*0.5)
    ny = (yy - H*0.5) / (H*0.5)
    r2 = nx*nx + ny*ny
    mask = np.clip(1.0 - strength * r2, 0.0, 1.0)
    out = (img.astype(np.float32) * mask[..., None]).astype(np.uint8)
    return out

def post_scanlines(img, strength=0.22):
    out = img.astype(np.float32)
    y = np.arange(H, dtype=np.float32)
    m = 1.0 - strength * (0.5 + 0.5*np.sin(2*np.pi*y/3.0))
    out *= m[:, None, None]
    return np.clip(out, 0, 255).astype(np.uint8)

def post_posterize(img, q=32):
    q = max(1, int(q))
    return ((img // q) * q).astype(np.uint8)

def background_hsv_gradient(img, t, scene_type="grey"):
    hsv = np.zeros((H, W, 3), np.uint8)
    ys = np.linspace(0, 1, H, dtype=np.float32)
    wave = 12 * np.sin(t * 1.2 + ys * 2.0)
    
    if scene_type == "grey":
        hsv[:, :, 0] = 0
        hsv[:, :, 1] = 0
        val = (35 + 40 * (1 - ys) + wave * 0.4).astype(np.float32)
        hsv[:, :, 2] = np.clip(val, 15, 90).astype(np.uint8)[:, None]
    elif scene_type == "red":
        hsv[:, :, 0] = 0  
        hsv[:, :, 1] = 160  
        val = (25 + 30 * (1 - ys) + wave * 0.4).astype(np.float32)
        hsv[:, :, 2] = np.clip(val, 10, 80).astype(np.uint8)[:, None]
    else:
        hsv[:, :, 0] = 0
        hsv[:, :, 1] = 80
        val = (30 + 35 * (1 - ys) + wave * 0.4).astype(np.float32)
        hsv[:, :, 2] = np.clip(val, 12, 85).astype(np.uint8)[:, None]
        
    img[:] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def scene_credits(img, t):
    background_hsv_gradient(img, t, scene_type="grey")
    rng = np.random.default_rng(1)
    xs = rng.integers(0, W, 380)
    ys = rng.integers(0, int(H*0.65), 380)
    colors = np.zeros((380, 3), dtype=np.uint8)
    colors[::3] = [50, 50, 240]  # BGR Rojo
    colors[1::3] = [220, 220, 220]  # BGR Blanco
    colors[2::3] = [160, 160, 160]  # BGR Gris
    img[ys, xs] = colors
    img[:] = cv2.GaussianBlur(img, (0,0), 0.6)
    
    cv2.putText(img, "DEMO PROCEDURAL", (42, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.95, (20, 20, 180), 5, cv2.LINE_AA)
    cv2.putText(img, "DEMO PROCEDURAL", (42, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.95, (80, 80, 255), 2, cv2.LINE_AA)
    cv2.putText(img, "Michael Aaron Villalon Nieves", (42, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (180, 180, 180), 2, cv2.LINE_AA)

def scene_lissajous(img, t):
    background_hsv_gradient(img, t, scene_type="red")
    a = 5 + 1.5 * math.sin(t*1.0)
    b = 4 + 1.2 * math.cos(t*1.2)
    delta = math.pi/4 + 0.8*math.sin(t*1.5)
    fx = lambda x: np.sin(a*x + delta)
    fy = lambda x: np.sin(b*x)
    pts = poly_param(fx, fy, 0, 2*math.pi, 1200, W*0.5, H*0.45, 300, 200)
    
    s_val = int(127 + 127 * math.sin(t * 2.5))
    col = hsv_to_bgr(0, s_val, 245)
    glow_col = hsv_to_bgr(0, 240, 160)
    
    # Renderizar silueta brillante y luego el centro más claro
    cv2.polylines(img, [pts], False, glow_col, 5, cv2.LINE_AA)
    cv2.polylines(img, [pts], False, col, 2, cv2.LINE_AA)

def scene_rose_polar(img, t):
    background_hsv_gradient(img, t, scene_type="grey")
    # Rosa polar: r = cos(k*theta)
    k = 6
    theta0 = t * 2.5
    fx = lambda th: np.cos(k*th) * np.cos(th + theta0)
    fy = lambda th: np.cos(k*th) * np.sin(th + theta0)
    pts = poly_param(fx, fy, 0, 2*math.pi, 1500, W*0.5, H*0.45, 270, 270)
    
    s_val = int(120 + 120 * math.sin(t * 1.8))
    col = hsv_to_bgr(0, s_val, 255)
    glow_col = hsv_to_bgr(0, 255, 150)
    
    cv2.polylines(img, [pts], False, glow_col, 5, cv2.LINE_AA)
    cv2.polylines(img, [pts], False, col, 2, cv2.LINE_AA)
    
    for i in range(8):
        r = int(22 + 15*np.sin(t*6.0 + i*0.8))
        color = (60, 60, 220) if i % 2 == 0 else (160, 160, 160)
        cv2.circle(img, (int(W*0.12 + i*90), int(H*0.82)), max(1, r), color, 2, cv2.LINE_AA)

def scene_spirograph(img, t):
    background_hsv_gradient(img, t, scene_type="red")
    # Hipotrocoide (spirograph): (R-r)cos(t) + d cos((R-r)/r * t)
    R, r, d = 13.0, 5.0, 8.0
    w = (R - r) / r
    fx = lambda x: (R-r)*np.cos(x) + d*np.cos(w*x + 0.4*np.sin(t*1.8))
    fy = lambda x: (R-r)*np.sin(x) - d*np.sin(w*x + 0.4*np.cos(t*1.5))
    pts = poly_param(fx, fy, 0, 16*math.pi, 2000, W*0.5, H*0.46, 18, 18)
    
    s_val = int(127 + 127 * math.sin(t * 1.5))
    col = hsv_to_bgr(0, s_val, 230)
    glow_col = hsv_to_bgr(0, 255, 160)
    
    cv2.polylines(img, [pts], False, glow_col, 5, cv2.LINE_AA)
    cv2.polylines(img, [pts], False, col, 2, cv2.LINE_AA)
    img[:] = post_scanlines(img, 0.18)

def scene_particles(img, t, rng):
    background_hsv_gradient(img, t, scene_type="grey")
    n = 1200
    xs = rng.random(n) * W
    ys = rng.random(n) * H
    xs = (xs + 110*np.sin(ys/55.0 + t*4.0) + 40*np.cos(t*1.8)) % W
    ys = (ys + 85*np.cos(xs/75.0 + t*3.0) + 30*np.sin(t*2.2)) % H
    v = (0.5 + 0.5*np.sin(t*4.0)).astype(float) if hasattr(t, "astype") else (0.5 + 0.5*math.sin(t*4.0))
    
    col_red = hsv_to_bgr(0, 240, int(200 + 55*v))
    col_grey = hsv_to_bgr(0, 15, int(200 + 55*v))
    
    img[ys[:600].astype(np.int32), xs[:600].astype(np.int32)] = col_red
    img[ys[600:].astype(np.int32), xs[600:].astype(np.int32)] = col_grey
    img[:] = cv2.GaussianBlur(img, (0,0), 1.1)

def scene_fire(img, t, state):
    heat = state["heat"]
    rng = state["rng"]
    heat[:] = (heat * 0.93).astype(np.float32)

    base_n = 1400
    xs = rng.integers(0, W, base_n)
    ys = rng.integers(int(H*0.82), H, base_n)
    heat[ys, xs] += rng.random(base_n) * (0.8 + 0.6*(0.5+0.5*math.sin(t*5.0)))

    heat[:] = cv2.GaussianBlur(heat, (0, 0), 2.2)
    heat[:-2, :] = heat[2:, :] 
    heat[-2:, :] *= 0.0

    h = np.zeros_like(heat, dtype=np.uint8)  
    s = (245 * (1.0 - np.clip(heat - 0.4, 0.0, 0.6) * 1.6)).astype(np.uint8)
    v = (15 + 240 * np.clip(heat, 0, 1)).astype(np.uint8)
    hsv = np.dstack([h, s, v]).astype(np.uint8)
    img[:] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    cv2.rectangle(img, (0, int(H*0.83)), (W, H), (20, 20, 20), -1)  # Gris carbón oscuro
    sparks = 160
    sx = rng.integers(0, W, sparks)
    sy = rng.integers(int(H*0.55), int(H*0.9), sparks)
    
    for idx in range(sparks):
        color = (40, 40, 240) if idx % 2 == 0 else (180, 180, 180)
        img[sy[idx], sx[idx]] = color
    img[:] = cv2.GaussianBlur(img, (0,0), 0.6)

def render_scene(buf, scene_id, t, rng, fire_state):
    if scene_id == 0:
        scene_credits(buf, t)
    elif scene_id == 1:
        scene_lissajous(buf, t)
    elif scene_id == 2:
        scene_rose_polar(buf, t)
    elif scene_id == 3:
        scene_spirograph(buf, t)
    elif scene_id == 4:
        scene_particles(buf, t, rng)
    else:
        scene_fire(buf, t, fire_state)

def timeline(t, rng, bufA, bufB, fire_state):
 
    block = int(min(5, max(0, t // 8)))
    t_in = t - block*8

    # Render escena base
    render_scene(bufA, block, t, rng, fire_state)
    frame = bufA

    if block < 5 and t_in >= 6.8:
        render_scene(bufA, block, t, rng, fire_state)
        render_scene(bufB, block+1, t, rng, fire_state)
        a = smoothstep(6.8, 8.0, t_in)
        frame = cv2.addWeighted(bufA, 1-a, bufB, a, 0)
        flash = smoothstep(7.6, 8.0, t_in)
        if flash > 0:
            frame = cv2.addWeighted(frame, 1.0, np.full_like(frame, 255), 0.12*flash, 0)

    fin = smoothstep(0.0, 1.5, t)
    fout = 1.0 - smoothstep(DURATION - 1.5, DURATION, t)
    f = fin * fout
    if f < 0.999:
        frame = (frame.astype(np.float32) * f).astype(np.uint8)
    return frame

def main():
    rng = np.random.default_rng(123)
    bufA = np.zeros((H, W, 3), np.uint8)
    bufB = np.zeros((H, W, 3), np.uint8)

    fire_state = {
        "heat": np.zeros((H, W), np.float32),
        "rng": np.random.default_rng(999),
    }

    total_frames = int(DURATION * FPS)
    
    #Exportación de video
    video_filename = 'demo.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_video = cv2.VideoWriter(video_filename, fourcc, FPS, (W, H))
    has_display = "DISPLAY" in os.environ

    t0 = time.perf_counter()
    for i in range(total_frames):
        t = i / FPS
        frame = timeline(t, rng, bufA, bufB, fire_state)
        frame = post_vignette(frame, 0.72)
        frame = post_scanlines(frame, 0.16)
        frame = post_posterize(frame, 24)
        
        out_video.write(frame)
        
        if has_display:
            cv2.imshow("Proyecto Final: demo procedural (OpenCV)", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                print("Exportación interrumpida por el usuario.")
                break
        else:
            if (i + 1) % 100 == 0 or i == total_frames - 1:
                print(f"Progreso de exportación: {i + 1}/{total_frames} fotogramas ({(i + 1)/total_frames*100:.1f}%)")
                
    out_video.release()
    print("Tiempo total de ejecución:", time.perf_counter() - t0)
    print(f"Vídeo exportado exitosamente a '{video_filename}'")
    if has_display:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
