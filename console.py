from main_controller import MainController

def main():
    controller = MainController()
    print("System initialized. Type 'exit' to quit.")

    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Exiting. Goodbye!")
                controller.shutdown()
                break

            responses = controller.communicate(user_input)
            for role, message in responses.items():
                print(f"{role.capitalize()}: {message}")

    except KeyboardInterrupt:
        print("\nSession interrupted. Exiting.")
        controller.shutdown()

if __name__ == "__main__":
    main()