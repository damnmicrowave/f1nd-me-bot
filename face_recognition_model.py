import numpy as np
import face_recognition
from PIL import Image, ImageDraw
import os
import pickle
import re


def face_distance(face_encodings, face_to_compare):
    if len(face_encodings) == 0:
        return np.empty(0)

    ans = []
    for face in face_encodings:
        scores = []
        for emb in face:
            scores.append(np.linalg.norm(emb - face_to_compare))
        ans.append(np.mean(np.array(scores)))

    return np.array(ans)


def compare_faces(known_face_encodings, face_encoding_to_check, tolerance=0.6):
    min_el = min(face_distance(known_face_encodings, face_encoding_to_check))
    min_s = np.argmin(face_distance(known_face_encodings, face_encoding_to_check))

    if min_el <= tolerance:
        return min_s
    else:
        return -1


def resize_image(input_image_path,
                 output_image_path,
                 size):
    original_image = Image.open(input_image_path)
    width, height = original_image.size

    resized_image = original_image.resize(size)
    width, height = resized_image.size

    resized_image.show()
    resized_image.save(output_image_path)


def transliterate(string):
    capital_letters = {u'А': u'A',
                       u'Б': u'B',
                       u'В': u'V',
                       u'Г': u'G',
                       u'Д': u'D',
                       u'Е': u'E',
                       u'Ё': u'E',
                       u'З': u'Z',
                       u'И': u'I',
                       u'Й': u'Y',
                       u'К': u'K',
                       u'Л': u'L',
                       u'М': u'M',
                       u'Н': u'N',
                       u'О': u'O',
                       u'П': u'P',
                       u'Р': u'R',
                       u'С': u'S',
                       u'Т': u'T',
                       u'У': u'U',
                       u'Ф': u'F',
                       u'Х': u'H',
                       u'Ъ': u'',
                       u'Ы': u'Y',
                       u'Ь': u'',
                       u'Э': u'E', }

    capital_letters_transliterated_to_multiple_letters = {u'Ж': u'Zh',
                                                          u'Ц': u'Ts',
                                                          u'Ч': u'Ch',
                                                          u'Ш': u'Sh',
                                                          u'Щ': u'Sch',
                                                          u'Ю': u'Yu',
                                                          u'Я': u'Ya', }

    lower_case_letters = {u'а': u'a',
                          u'б': u'b',
                          u'в': u'v',
                          u'г': u'g',
                          u'д': u'd',
                          u'е': u'e',
                          u'ё': u'e',
                          u'ж': u'zh',
                          u'з': u'z',
                          u'и': u'i',
                          u'й': u'y',
                          u'к': u'k',
                          u'л': u'l',
                          u'м': u'm',
                          u'н': u'n',
                          u'о': u'o',
                          u'п': u'p',
                          u'р': u'r',
                          u'с': u's',
                          u'т': u't',
                          u'у': u'u',
                          u'ф': u'f',
                          u'х': u'h',
                          u'ц': u'ts',
                          u'ч': u'ch',
                          u'ш': u'sh',
                          u'щ': u'sch',
                          u'ъ': u'',
                          u'ы': u'y',
                          u'ь': u'',
                          u'э': u'e',
                          u'ю': u'yu',
                          u'я': u'ya', }

    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.items():
        string = re.sub("%s([а-я])" % cyrillic_string, '%s\1' % latin_string, string)

    for dictionary in (capital_letters, lower_case_letters):
        for cyrillic_string, latin_string in dictionary.items():
            string = string.replace(cyrillic_string, latin_string)

    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.items():
        string = string.replace(cyrillic_string, latin_string.upper())

    return string


class FaceR:
    def __init__(self):
        self.user_name = "Me"
        self.user_face_encoding = []

        self.users_names = []
        self.users_id = []
        self.users_face_encoding = []

    def user_photo(self, source, photo):
        image = face_recognition.load_image_file(source + photo)
        face_encodings = face_recognition.face_encodings(image)
        self.user_face_encoding = face_encodings

        return 200

    def users_photos(self, source, photos):
        for photo in photos:

            image = face_recognition.load_image_file(source + photo)
            face_encodings = face_recognition.face_encodings(image)

            if len(face_encodings) == 1:
                self.users_face_encoding.append([face_encodings])
                name = photo[:photo.index('@')]
                id_ = photo[photo.index('@'):-4]
                self.users_names.append(name)
                self.users_id.append(id_)

        with open("names", "wb") as file:
            pickle.dump(self.users_names, file)

        with open("ids", "wb") as file:
            pickle.dump(self.users_id, file)

        with open("encodings", "wb") as file:
            pickle.dump(self.users_face_encoding, file)

        return 200

    def pickle_down(self):
        with open("names", "rb") as file:
            self.users_names = pickle.load(file)

        with open("ids", "rb") as file:
            self.users_id = pickle.load(file)

        with open("encodings", "rb") as file:
            self.users_face_encoding = pickle.load(file)

        return 200

    def album_recog(self, vk_imgs):
        names_img = []

        for img in vk_imgs:
            image = face_recognition.load_image_file(source_2 + img)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            pil_image = Image.fromarray(image)
            pil_image_original = Image.fromarray(image)

            draw = ImageDraw.Draw(pil_image)
            flag = False

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = compare_faces(np.array(self.users_face_encoding), np.array(face_encoding), tolerance=0.6)
                matches_user = compare_faces(np.array(self.user_face_encoding), np.array(face_encoding), tolerance=0.6)

                if matches_user != -1:
                    flag = True
                    name = "ME"
                    draw.rectangle(((left, top), (right, bottom)), outline=(0, 178, 255))
                    text_width, text_height = draw.textsize(name)
                    draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 178, 255),
                                   outline=(0, 0, 255))
                    draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

                if matches != -1:
                    self.users_face_encoding[matches].append(face_encoding)
                    name = transliterate(self.users_names[matches])
                    draw.rectangle(((left, top), (right, bottom)), outline=(0, 178, 255))
                    text_width, text_height = draw.textsize(name)
                    draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 178, 255),
                                   outline=(0, 0, 255))
                    draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

            if flag:
                pil_image.save("./me_photo/" + img[:-4] + "_marked", format="png")
                names_img.append("me_photo/" + img[:-4] + "_marked.png")
                pil_image_original.save("./me_photo/" + img[:-4] + "_orig", format="png")
                names_img.append("me_photo/" + img[:-4] + "_orig.png")
            del draw

        return names_img


Model = FaceR()

source = "users/"
photos = [i for i in os.listdir(source) if i[-4:] == '.jpg']
Model.users_photos(source, photos)

source_2 = "groups/-80270762/GoTo Camp Summer 07_2018"
vk_imgs = [i for i in os.listdir(source_2)]
Model.album_recog(vk_imgs)

source_3 = "user_face/"
photo_name = "face.jpg"
Model.user_photo(source_3, photo_name)
