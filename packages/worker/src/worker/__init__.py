from worker.proc import app


def main():
    app.run_worker(concurrency=1)


__all__ = ["app"]


if __name__ == "__main__":
    main()
