import numpy as np
from io import BytesIO
from PIL import Image


class Texture():

    folder = None

    def __init__(self, textureUri, objects_type, cursor, triangles):
        """
        :param textureUri : a texture Uri in the database
        :param objects_type: a class name among CityMCityObject derived classes.
                        For example, objects_type can be "CityMBuilding".
        :param cursor: a database access cursor
        Create a pillow.image:
        """
        imageBinaryData = objects_type.retrieve_textures(
            cursor,
            textureUri,
            objects_type)
        LEFT_THUMB = imageBinaryData[0][0]
        stream = BytesIO(LEFT_THUMB)
        image = Image.open(stream).convert("RGBA")

        self.texture_image = self.cropImage(image, triangles)

    def get_texture_image(self):
        return self.texture_image

    def cropImage(self, image, triangles):
        minX = 2
        maxX = -1

        minY = 2
        maxY = -1

        texture_size = image.size
        for uv_triangle in triangles:
            for uv in uv_triangle:
                if uv[0] < minX:
                    minX = uv[0]
                if uv[0] > maxX:
                    maxX = uv[0]
                if uv[1] < minY:
                    minY = uv[1]
                if uv[1] > maxY:
                    maxY = uv[1]

        cropped_image = image.crop((minX * texture_size[0], minY * texture_size[1], maxX * texture_size[0], maxY * texture_size[1]))

        self.updateUvs(triangles, [minX, minY, maxX, maxY])
        return cropped_image

    def updateUvs(self, uvs, rect):
        offsetX = rect[0]
        offsetY = rect[1]
        if rect[2] != rect[0]:
            ratioX = 1 / (rect[2] - rect[0])
        else:
            ratioX = 1
        if rect[3] != rect[1]:
            ratioY = 1 / (rect[3] - rect[1])
        else:
            ratioY = 1

        for i in range(0, len(uvs)):
            for y in range(0, 3):
                new_u = (uvs[i][y][0] - offsetX) * ratioX
                new_v = (uvs[i][y][1] - offsetY) * ratioY
                # warning : in order to be written correctly, the GLTF writter
                # expects data to be in float32
                uvs[i][y] = np.array([new_u, new_v], dtype=np.float32)

    @staticmethod
    def get_texture_folder():
        return Texture.folder

    @staticmethod
    def set_texture_folder(folder):
        Texture.folder = folder