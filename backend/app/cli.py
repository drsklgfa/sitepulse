from app.database import SessionLocal, init_db
from app.seed import seed_demo


def main() -> None:
    init_db()
    with SessionLocal() as db:
        seed_demo(db)
    print("Dados demonstrativos criados com sucesso.")


if __name__ == "__main__":
    main()
