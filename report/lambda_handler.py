from report import generate_report


def handler(event=None, context=None) -> dict:

    report_html = generate_report()

    return {
        "statusCode": 200,
        "body": report_html
    }


if __name__ == "__main__":
    pass
