from core.schema import LabelEntry, PackConfig


def test_pack_config_creation():
    pack = PackConfig(
        pack_name="animals",
        display_name="Animals",
        description="Test pack",
        labels=[LabelEntry(id="dog", text="dog", aliases=["puppy"])],
    )

    assert pack.pack_name == "animals"
    assert pack.labels[0].id == "dog"
    assert pack.labels[0].text == "dog"