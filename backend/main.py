from app.main import app

__all__ = ["app"]


def main() -> None:
    print("GeoAttend backend is configured. Run `fastapi dev main.py` to start.")


if __name__ == "__main__":
    main()
