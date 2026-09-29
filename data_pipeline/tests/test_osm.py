from data_pipeline.ingestion.osm import read_osm_xml


def test_incomplete_ways_are_not_invented():
    xml = b'<osm><node id="1" lon="74" lat="16"/><way id="1"><nd ref="1"/><nd ref="2"/><tag k="waterway" v="river"/></way></osm>'
    assert read_osm_xml(xml) == []


def test_only_required_transport_and_waterways_are_selected():
    xml = b'<osm><node id="1" lon="74" lat="16"/><node id="2" lon="74.1" lat="16.1"/><way id="1"><nd ref="1"/><nd ref="2"/><tag k="waterway" v="river"/></way><way id="2"><nd ref="1"/><nd ref="2"/><tag k="highway" v="residential"/></way></osm>'
    rows = read_osm_xml(xml)
    assert len(rows) == 1
    assert rows[0]["kind"] == "river"
