import os


def check_project_id(name, project_id):
    """
    Function to check if a project ID was selected by the user
    """
    if project_id == "":
        final_name = name
    else:
        final_name = f"{name} - {project_id}"

    return final_name


def check_mapping_group(mapping_group_name, mapping_group):
    """
    Function to check if a group exists and rename it
    """
    found_group = mapping_group.findGroup(mapping_group_name)

    if found_group:
        count = 1
        new_group_name = f"{mapping_group_name} ({count})"
        while mapping_group.findGroup(new_group_name):
            count += 1
            new_group_name = f"{mapping_group_name} ({count})"
        mapping_group = mapping_group.insertGroup(0, new_group_name)
    else:
        mapping_group = mapping_group.insertGroup(0, mapping_group_name)

    return mapping_group


def check_raster_file(raster_name, map_output_dir):
    """
    Function to check if a raster exits, if so rename it
    """

    original_raster_path = os.path.join(map_output_dir, f"{raster_name}.tif")

    if os.path.exists(original_raster_path):
        count = 1
        new_raster_name = f"{raster_name} ({count})"
        new_raster_path = os.path.join(map_output_dir, f"{new_raster_name}.tif")

        while os.path.exists(new_raster_path):
            count += 1
            new_raster_name = f"{raster_name} ({count})"
            new_raster_path = os.path.join(map_output_dir, f"{new_raster_name}.tif")

        return new_raster_name, new_raster_path
    else:
        return raster_name, original_raster_path

def check_vector_file(vector_name, map_output_dir):
    """
    Function to check if a vector exits, if so rename it
    """

    original_vector_path = os.path.join(map_output_dir, f"{vector_name}.shp")

    if os.path.exists(original_vector_path):
        count = 1
        new_vector_name = f"{vector_name} ({count})"
        new_vector_path = os.path.join(map_output_dir, f"{new_vector_name}.shp")

        while os.path.exists(new_vector_path):
            count += 1
            new_vector_name = f"{vector_name} ({count})"
            new_vector_path = os.path.join(map_output_dir, f"{new_vector_name}.shp")

        return new_vector_name, new_vector_path
    else:
        return vector_name, original_vector_path

