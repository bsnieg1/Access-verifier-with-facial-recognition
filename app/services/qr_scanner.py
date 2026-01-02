import cv2

qr_detector = cv2.QRCodeDetector()


def scan_qr(frame, draw_bbox=False):
    data, bbox, _ = qr_detector.detectAndDecode(frame)

    if not data:
        return None

    if bbox is not None and draw_bbox:
        pts = bbox.astype(int).reshape(-1, 2)
        n = len(pts)
        for i in range(n):
            pt1 = tuple(pts[i])
            pt2 = tuple(pts[(i + 1) % n])
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

        cv2.putText(frame, f"QR: {data}", (pts[0][0], pts[0][1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    return data