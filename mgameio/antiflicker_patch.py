from pathlib import Path

p = Path("build/main.go")
s = p.read_text(encoding="utf-8")

def replace_once(old, new):
    global s
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f"Expected one occurrence, found {n}: {old[:70]!r}")
    s = s.replace(old, new, 1)

replace_once('var procEndPaint = user.NewProc("EndPaint")', 'var procEndPaint = user.NewProc("EndPaint")\nvar procGetClientRect = user.NewProc("GetClientRect")')
replace_once('var procCreateBrush = gdi.NewProc("CreateSolidBrush")', '''var procCreateBrush = gdi.NewProc("CreateSolidBrush")
var procCreateCompatibleDC = gdi.NewProc("CreateCompatibleDC")
var procCreateCompatibleBitmap = gdi.NewProc("CreateCompatibleBitmap")
var procBitBlt = gdi.NewProc("BitBlt")
var procDeleteDC = gdi.NewProc("DeleteDC")''')
replace_once('func paintHome(hdc uintptr) {', '''// Draw the complete frame off-screen, then atomically present it to Windows.
// Prevents the background/cards/text from flashing during status updates.
func paintBuffered(hwnd, screenDC uintptr) {
    var bounds winRect
    if ok, _, _ := procGetClientRect.Call(hwnd, uintptr(unsafe.Pointer(&bounds))); ok == 0 { paint(screenDC); return }
    width, height := int(bounds.Right-bounds.Left), int(bounds.Bottom-bounds.Top)
    if width < 1 || height < 1 { return }
    memDC, _, _ := procCreateCompatibleDC.Call(screenDC)
    if memDC == 0 { paint(screenDC); return }
    defer procDeleteDC.Call(memDC)
    bmp, _, _ := procCreateCompatibleBitmap.Call(screenDC, uintptr(width), uintptr(height))
    if bmp == 0 { paint(screenDC); return }
    old, _, _ := procSelectObject.Call(memDC, bmp)
    drawRect(memDC, 0, 0, width, height, 0, colorBG)
    paint(memDC)
    procBitBlt.Call(screenDC, 0, 0, uintptr(width), uintptr(height), memDC, 0, 0, 0x00CC0020)
    procSelectObject.Call(memDC, old)
    procDeleteObject.Call(bmp)
}
func paintHome(hdc uintptr) {''')
replace_once('paint(hdc)\n\t\tprocEndPaint.Call(hwnd', 'paintBuffered(hwnd, hdc)\n\t\tprocEndPaint.Call(hwnd')
replace_once('''        refreshTick++
        if page == 7 && refreshTick%2 == 0 { pollWindows() }
        refresh()
        return 0''', '''        refreshTick++
        // Requery window list only while this section is visible.
        if page == 7 && refreshTick%2 == 0 { pollWindows() }
        return 0''')
replace_once('''        refresh()
        return 0
    case WM_APP_WINDOWS:''', '''        // Live stats are visible on these pages only.
        if page == 0 || page == 2 || page == 11 { refresh() }
        return 0
    case WM_APP_WINDOWS:''')
replace_once('v2.1  •  WINDOWS', 'v2.2  •  WINDOWS')
replace_once('Версия 2.1 · Windows 10/11', 'Версия 2.2 · Windows 10/11')
p.write_text(s, encoding="utf-8")
print("MgameIO 2.2: double-buffered drawing and selective refresh applied.")
