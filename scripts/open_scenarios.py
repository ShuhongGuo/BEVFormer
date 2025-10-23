#!/usr/bin/env python3
"""
Construct URLs by replacing scenario_id from a list and:
 - print each full URL (with fragment)
 - try to open it with xdg-open (best-effort; may fail on headless servers)
 - send an HTTP GET to the base URL (fragment removed) and print the status code

Usage: python3 scripts/open_scenarios.py
"""
import subprocess
import requests
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# scenario IDs extracted from the screenshots — these will replace the scenario_id in the
# bet_viewer URL template.
# scenario_ids = [
#     "20250427_p7040_130201_1745733923",
#     "20230916_g8026_071109_1694828177",
#     "20221204_p6066_123608_1670130434",
#     "20230916_g8028_114654_1694838972",
#     "20230716_g8019_114059_1689487569",
#     "20230524_g8027_151358_1684916305",
#     "20250808_k9038_072056_1754615655",
#     "20231216_p6054_091142_1702698311",
#     "20250710_k0142_073423_1752106987",
#     "20250425_k9014_144357_1745571684",
#     "20250507_k9013_072028_1746581020",
#     "20230623_p6065_080129_1687482859",
#     "20250908_k8025_163724_1757321162",
#     "20231008_p6122_152758_1696751361",
#     "20230625_g8008_184632_1687696779",
#     "20230905_p7014_161712_1693903999",
#     "20240223_p6122_203214_1708693313",
#     "20230910_g8004_150306_1694345376",
# ]

# New bet_viewer URL template — we'll replace SCENARIO_ID placeholder with each id
url_template = (
    "https://ppov-web.k8s.corp.pony.ai:30443/#record_path=/guangzhou/bet_v2/report/bet_pr_report/perception_critical_missing/59243"
    "&app=bet_viewer&app_gflags=--use_hdfs%20--scenario_id%20%22SCENARIO_ID%22%20--evaluation_mode%20PERCEPTION%20--data_set%20CRITICAL_MISSING_DATASET%20--load_remote_config%20--use_roi_async_loader%20--enable_tile_based_road_graph%20--enable_using_router_road_graph%20--enable_tile_based_rg_incremental_view_switch%20--road_graph_any_version%20--static_map_any_version%20--use_truncated_map_data%20--enable_eval_stats_widget%20--enable_lidar_data_v3%20--default_metric%20CRITICAL_REDUNDANT_COUNT%20--evaluation_submode%20CRITICAL_MISSING%20--default_filter_condition=%22outside_no_label_zone:true;range:60.0;roi_ext:8.0;%22%20--baseline_report_url%20/guangzhou/bet_v2/report/bet_pr_report/perception_critical_missing/59242&suite_path=&play=true"
)

url_template = (
  'https://ppov-web.k8s.corp.pony.ai:30443/#record_path=common/config/simulation/brt/SCENARIO_ID.config&app=regression_debug&app_gflags=--use_unified_memory_by_default%20--use_unified_memory_for_inference%20--pause_on_start%20--road_graph_any_version%20--static_map_any_version%20--regression_jobid_list%3Dguangzhou%3Apr%3A42231%2Cguangzhou%3Apr%3A42241&suite_path=&play=true'  
)

    # brt paths extracted from the screenshot (in the same top->down order)
brt_path = [
        # "perception/nansha/20250817/20250817_k8019_1755394638_1755394665",
        # "perception/nansha/20250721/20250721_g8020_1753085856_1753085883",
        # "perception/nansha/20250730/20250730_p7033_1753869249_1753869271",
        # "perception/nansha/20241120/20241120_g8011_1732070297_1732070324",
        # "perception/yizhuang/20240826/20240826_p7016_1724644107_1724644132",
        # "perception/nansha/20240906/20240906_g8012_1725596021_1725596046",
        # "perception/yizhuang/20241101/20241101_p7014_1730464282_1730464414",
        # "perception/nansha/20241119/20241119_p7049_1731982717_1731982744",
        # "perception/yizhuang/20250114/20250114_p6078_1736840007_1736840029",
        # "perception/nansha/20241114/20241114_p6016_1731578301_1731578328",
        # "perception/nansha/20241025/20241025_p7010_1729858989_1729859015",
        # "perception/yizhuang/20240801/20240801_p6050_1722491412_1722491437",
        # "perception/nansha/20240612/20240612_p7047_1718201022_1718201046",
        # "perception/nansha/20240517/20240517_p6009_1715931771_1715931796",
        # "perception/yizhuang/20240421/20240421_p7004_1713666749_1713666773",
        # "perception/yizhuang/20240329/20240329_p7012_1711701276_1711701300",
        # "perception/yizhuang/20240315/20240315_g8034_1710508836_1710508861",
        # "perception/nansha/20230704/20230704_g8005_1688440092_1688440117",
        # "perception/yizhuang/20240410/20240410_p6085_1712747848_1712747872",
        # "perception/yizhuang/20240410/20240410_p6085_1712749221_1712749245",
]

# Additional paths from the latest screenshot (appended, top->down order)
additional_brt = [
    "perception/nansha/20250817/20250817_k8019_1755394638_1755394665",
    "perception/nansha/20250721/20250721_g8020_1753085856_1753085883",
    "perception/nansha/20250730/20250730_p7033_1753869249_1753869271",
    "perception/nansha/20250713/20250713_p6001_1752406365_1752406392",
    "perception/nansha/20241120/20241120_g8011_1732070297_1732070324",
    "perception/yizhuang/20240826/20240826_p7016_1724644107_1724644132",
    "perception/nansha/20240906/20240906_g8012_1725596021_1725596046",
    "perception/yizhuang/20241101/20241101_p7014_1730464282_1730464414",
    "perception/nansha/20241119/20241119_p7049_1731982717_1731982744",
    "perception/yizhuang/20250222/20250222_p6097_1740209162_1740209189",
    "perception/yizhuang/20241022/20241022_p7012_1729572737_1729572764",
    "perception/nansha/20241025/20241025_p7010_1729858989_1729859015",
    "perception/nansha/20240925/20240925_p7021_1727271415_1727271440",
    "perception/nansha/20240811/20240811_g8007_1723363164_1723363189",
    "perception/yizhuang/20240801/20240801_p6050_1722491412_1722491437",
    "perception/yizhuang/20240611/20240611_p6044_1718068247_1718068271",
    "perception/nansha/20240517/20240517_p6009_1715931771_1715931796",
    "perception/nansha/20240429/20240429_p6019_1714373310_1714373335",
    "perception/yizhuang/20240421/20240421_p7004_1713666749_1713666773",
    "perception/nansha/20240506/20240506_p7048_1715002640_1715002664",
    "perception/yizhuang/20240421/20240421_p7004_1713666443_1713666468",
    "perception/yizhuang/20240329/20240329_p7012_1711701276_1711701300",
    "perception/nansha/20230704/20230704_g8005_1688440092_1688440117",
    "perception/yizhuang/20240410/20240410_p6085_1712747848_1712747872",
    "perception/yizhuang/20240410/20240410_p6085_1712749221_1712749245",
    "perception/yizhuang/20240410/20240410_p6085_1712747845_1712747869",
    "perception/yizhuang/20240407/20240407_p6048_1712464423_1712464448",
    "perception/yizhuang/20240318/20240318_p6043_1710766816_1710766841",
    "perception/nansha/20240328/20240328_p6004_1711603753_1711603773",
    "perception/yizhuang/20240320/20240320_p6053_1710934749_1710934774",
    "perception/nansha/20240303/20240303_p7022_1709451557_1709451582",
    "perception/nansha/20230920/20230920_p7030_1695184947_1695184972",
    "perception/nansha/20230922/20230922_g8008_1695380133_1695380158",
    "perception/nansha/20230705/20230705_g8018_1688550673_1688550698",
    "perception/nansha/20230718/20230718_g8018_1689646273_1689646298",
    "perception/nansha/20230713/20230713_g8004_1689209813_1689209838",
    "perception/yizhuang/20230831/20230831_p7004_1693454286_1693454311",
    "perception/yizhuang/20230811/20230811_p7012_1691716730_1691716754",
    "perception/nansha/20230709/20230709_p7030_1688873732_1688873757",
    "perception/nansha/20230521/20230521_g8028_1684668847_1684668872",
    "perception/yizhuang/20230430/20230430_p7044_1682829953_1682829978",
    "perception/nansha/20230328/20230328_p7042_1679972097_1679972122",
    "perception/yizhuang/20230119/20230119_p7008_1674114049_1674114074",
    "perception/yizhuang/20230131/20230131_p7044_1675166188_1675166213",
    "perception/nansha/20221213/20221213_g8007_1670905061_1670905086",
    "perception/nansha/20221221/20221221_g8001_1671622511_1671622536",
    "perception/nansha/20220809/20220809_g8099_1660048872_1660048940",
]

xx = ""
for sid in additional_brt:
    xx += sid + ','

print(xx)

# Append any additional entries that are not already present in brt_path
for p in additional_brt:
    if p not in brt_path:
        brt_path.append(p)
print("Will attempt to open and GET each constructed URL.\n")

for sid in brt_path:
    full_url = url_template.replace("SCENARIO_ID", sid)
    print('---')
    print('Full URL:')
    print(full_url)

    # Try to open with xdg-open (best-effort)
    try:
        subprocess.Popen(["xdg-open", full_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print('xdg-open invoked (may open a browser on the local machine).')
    except Exception as e:
        print('xdg-open failed:', e)

    # Do an HTTP GET to the base URL (fragment is client-side and not sent to server)
    base_url = full_url.split('#', 1)[0]
    try:
        r = requests.get(base_url, timeout=10, verify=False)
        print('GET ->', base_url, 'Status:', r.status_code)
    except Exception as e:
        print('HTTP GET error:', repr(e))

    # small pause to avoid spamming
    time.sleep(0.5)

print('\nDone.')
