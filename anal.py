# Main loop
while True:
    try:
        data, addr = sock.recvfrom(1024)
        print(f"\n📨 Received from {addr}: {data}")

        cmd = json.loads(data.decode())
        print(f"🧾 Parsed command: {cmd}")

        # Handle movement
        move = cmd.get("move")
        if move:
            print(f"> 🕹 Move command: {move}")

        if move == "forward":
            avancer()
        elif move == "backward":
            reculer()
        elif move == "left":
            gauche()
        elif move == "right":
            droite()
        elif move == "stop":
            stop()

        # Handle servo controls
        yaw = cmd.get("yaw")
        pitch = cmd.get("pitch")

        if yaw is not None:
            print(f"> 🎯 Yaw command: {yaw}")
            yaw_pulse = int(max(MIN_PULSE, min(MAX_PULSE, 1500 + yaw)))
            pi.set_servo_pulsewidth(SERVO_YAW, yaw_pulse)

        if pitch is not None:
            print(f"> 📷 Pitch command: {pitch}")
            pitch_pulse = int(max(MIN_PULSE, min(MAX_PULSE, 1500 - pitch)))
            pi.set_servo_pulsewidth(SERVO_PITCH, pitch_pulse)

    except Exception as e:
        print("❌ Error:", e)
        stop()
