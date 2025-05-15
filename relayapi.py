import RPi.GPIO as GPIO
from fastapi import FastAPI, HTTPException
import uvicorn
import time
from threading import Thread  # To handle the delay without blocking

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Define GPIO pins connected to the relay
relay_pins = [17, 27, 22, 23]  # Change these based on your GPIO connections

# Set up each relay pin as an output
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT)
    
# FastAPI app
app = FastAPI()

# Function to control relay: turn ON, wait for 5 seconds, and then turn OFF
def control_relay_action(pin: int):
    if pin not in relay_pins:
        raise ValueError("Invalid pin")
    GPIO.output(pin, GPIO.HIGH)  # Turn ON relay
    time.sleep(2)                # Wait for 3 seconds
    GPIO.output(pin, GPIO.LOW)   # Turn OFF relay
    
@app.post("/control/relay/{pin}")
async def control_relay(pin: int):
    if pin not in relay_pins:
        raise HTTPException(status_code=404, detail="Pin not found")
    # Run the relay control in a separate thread to avoid blocking the API
    thread = Thread(target=control_relay_action, args=(pin,))
    thread.start()
    return {"message": f"Relay {pin} lifted (ON) and will lower (OFF) in few seconds."}

@app.on_event("shutdown")
def shutdown():
    GPIO.cleanup()  # Clean up GPIO settings on shutdown
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8070)
