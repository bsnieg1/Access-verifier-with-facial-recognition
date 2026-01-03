def verify_face_for_user(
    frame,
    user_id: int,
    verifier,
    threshold: float = 0.6
) -> bool:
    
    result = verifier.verify_for_user(frame, user_id, threshold)
    
    if result.get("error"):
        print(f" Błąd: {result['error']}")
    
    return result["match"]
