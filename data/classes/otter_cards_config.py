

class OtterCardsConfig:

    settings = {
        "already_run_app": 0,
        "granted_camera_permission": 0,
        "granted_internet_permission": 0,
        "granted_storage_permission": 0
    }

    filename = ""

    @staticmethod
    def append(key: str, value: int):
        OtterCardsConfig.settings[key] = value

    @staticmethod
    def save():
        with open(OtterCardsConfig.filename, "w") as f:
            for key in OtterCardsConfig.settings.keys():
                f.write(f"{key} {OtterCardsConfig.settings[key]}\n")

    @staticmethod
    def read(file_name: str):
        if ".ini" not in file_name:
            raise ValueError

        OtterCardsConfig.filename = file_name

        with open(file=file_name) as f:
            for line in f.readlines():
                kw, v = line.split(" ")
                v = int(v)

                OtterCardsConfig.settings[kw] = v
