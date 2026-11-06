import time
import random
import threading

# Simulate a network environment where devices broadcast signals
class NetworkSimulator:
    def __init__(self):
        self.devices = {}
        self.lock = threading.Lock()

    def register_device(self, device_id, device_type):
        with self.lock:
            self.devices[device_id] = {'type': device_type, 'online': True, 'last_seen': time.time()}
            print(f"[Network] Device {device_id} ({device_type}) registered.")

    def unregister_device(self, device_id):
        with self.lock:
            if device_id in self.devices:
                self.devices[device_id]['online'] = False
                print(f"[Network] Device {device_id} went offline.")

    def broadcast_signal(self, sender_id, signal_data):
        # Simulate signal propagation
        with self.lock:
            if sender_id in self.devices and self.devices[sender_id]['online']:
                print(f"[Network] Signal from {sender_id}: {signal_data}")
                # Update last seen for all devices that 'hear' this signal
                for device_id, data in self.devices.items():
                    if data['online']:
                        data['last_seen'] = time.time()
            else:
                print(f"[Network] Device {sender_id} is offline, cannot broadcast.")

    def get_device_status(self, device_id):
        with self.lock:
            return self.devices.get(device_id)

# Simulate an IoT device that discovers others via signals
class IoTDevice:
    def __init__(self, device_id, device_type, network):
        self.device_id = device_id
        self.device_type = device_type
        self.network = network
        self.known_devices = {}
        self.is_online = True
        self.network.register_device(self.device_id, self.device_type)

    def send_heartbeat(self):
        # Periodically send a signal to indicate presence
        while self.is_online:
            signal = f"Heartbeat from {self.device_id} ({self.device_type})"
            self.network.broadcast_signal(self.device_id, signal)
            time.sleep(random.uniform(2, 5)) # Simulate varying broadcast intervals

    def discover_devices(self):
        # In a real scenario, this would involve listening for signals and processing them
        # For this simulation, we'll check the network's state periodically
        while self.is_online:
            current_time = time.time()
            print(f"[{self.device_id}] Scanning network...")
            for dev_id, data in self.network.devices.items():
                if dev_id != self.device_id:
                    if data['online'] and current_time - data['last_seen'] < 10: # Threshold for being considered 'online'
                        if dev_id not in self.known_devices:
                            print(f"[{self.device_id}] Discovered new device: {dev_id} ({data['type']})")
                            self.known_devices[dev_id] = {'type': data['type'], 'last_seen': data['last_seen']}
                        else:
                            # Update last seen if already known
                            self.known_devices[dev_id]['last_seen'] = data['last_seen']
                    elif dev_id in self.known_devices and (not data['online'] or current_time - data['last_seen'] >= 10):
                        # Device is no longer considered online
                        print(f"[{self.device_id}] Device {dev_id} ({data['type']}) seems to be offline or lost.")
                        del self.known_devices[dev_id]
            time.sleep(5) # Scan interval

    def go_offline(self):
        self.is_online = False
        self.network.unregister_device(self.device_id)
        print(f"[{self.device_id}] Device is going offline.")

# --- Simulation Setup ---
if __name__ == "__main__":
    network = NetworkSimulator()

    # Create some IoT devices
    device1 = IoTDevice("dev-001", "sensor", network)
    device2 = IoTDevice("dev-002", "actuator", network)
    device3 = IoTDevice("dev-003", "gateway", network)

    # Start device threads
    heartbeat_thread1 = threading.Thread(target=device1.send_heartbeat)
    discovery_thread1 = threading.Thread(target=device1.discover_devices)

    heartbeat_thread2 = threading.Thread(target=device2.send_heartbeat)
    discovery_thread2 = threading.Thread(target=device2.discover_devices)

    heartbeat_thread3 = threading.Thread(target=device3.send_heartbeat)
    discovery_thread3 = threading.Thread(target=device3.discover_devices)

    heartbeat_thread1.start()
    discovery_thread1.start()
    heartbeat_thread2.start()
    discovery_thread2.start()
    heartbeat_thread3.start()
    discovery_thread3.start()

    print("\n--- Simulation Running ---")
    time.sleep(15) # Let devices discover each other

    print("\n--- Simulating Device 2 Going Offline ---")
    device2.go_offline()
    time.sleep(10) # Allow other devices to detect the offline status

    print("\n--- Simulating Device 2 Coming Back Online ---")
    # Re-register and restart threads for device2 to simulate reconnection
    device2 = IoTDevice("dev-002", "actuator", network)
    heartbeat_thread2 = threading.Thread(target=device2.send_heartbeat)
    discovery_thread2 = threading.Thread(target=device2.discover_devices)
    heartbeat_thread2.start()
    discovery_thread2.start()

    time.sleep(15) # Allow devices to discover the reconnected device

    print("\n--- Simulation Ended ---")
    # In a real app, you'd have a proper shutdown mechanism
    device1.go_offline()
    device3.go_offline()
    device2.go_offline()

    heartbeat_thread1.join()
    discovery_thread1.join()
    heartbeat_thread2.join()
    discovery_thread2.join()
    heartbeat_thread3.join()
    discovery_thread3.join()
