from huggingface_hub import HfApi

api = HfApi()
api.upload_file(
    path_or_fileobj="/projects/p32364/Metaverse-R1/data.tar.gz.part-ab",
    path_in_repo="subset_data.tar.gz.part-ab",
    repo_id="zhenyupan/3d_layout_reasoning",
    repo_type="dataset",
)
# api.upload_file(
#     path_or_fileobj="/projects/p32364/Metaverse-R1/data.tar.gz.part-bb",
#     path_in_repo="subset_data.tar.gz.part-bb",
#     repo_id="zhenyupan/3d_layout_reasoning",
#     repo_type="dataset",
# )