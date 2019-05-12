from Crypto.Cipher import AES
import base64

'''
  CGV web service use AES which is a kind of symetric key encryption algorithm in order to securely pass parameters containing private or even confidential information when client makes a reservation for a movie on the website. 
  of particular interest is how the encryption algorithm is implemented. .net javascript framework has been so used to implement the encryption that it was not difficult to find out detailed specification of the AES algorithm with the microsoft .net framework official document and with reverse enginearing client-side script.
  AES algorithm cannot be competible of communication among different services without any specification of implementation detail such as block size, encryption key, block cipher modes of operation, initial vector and padding method etc.
  the CGV AES detailed specification is the table below.

  block size        : 16byte (128 bits)
  key size          : 32byte (256 bits)
  encryption key    : VBA1NUS6T8UID2I6OBF7158899CT4F3C
  initial_vector    : VBA1NUS6T8UID2I6
  block cipher mode : CBC
  encoding          : utf8
  wrapper           : base64
  padding           : PKCS7 (padding with sequence of bytes, each of which is equal to the size of padding bytes added)


'''

correct_input = "20190514"
correct_output = "uU8HUn3rxCYRKgs3pGahCA=="
cgv_aes_key = bytes([86, 66, 65, 49, 78, 85, 83, 54, 84, 56, 85, 73, 68, 50, 73, 54, 79, 66, 70, 55, 49, 53, 56, 56, 57, 57, 67, 84, 52, 70, 51, 67])
cgv_aes_IV = bytes([86, 66, 65, 49, 78, 85, 83, 54, 84, 56, 85, 73, 68, 50, 73, 54])

class cgv_crypto :
  def __init__(self, block_size=16, key=cgv_aes_key, IV=cgv_aes_IV, mode=AES.MODE_CBC) :
    self.BLOCK_SIZE = block_size
    self.encryption_mode = mode
    self.mode = mode
    self.key = key
    self.initial_vector = IV
    self.encryptor = self.make_encryptor()

  #PKCS7 padding method
  def pad(self, data) :
    padding_value = (self.BLOCK_SIZE-len(data))%self.BLOCK_SIZE
    padded_length = len(data) + padding_value
    padded_data = (data+bytes([padding_value])*self.BLOCK_SIZE)[:padded_length]
    return padded_data

  def make_encryptor(self) :
    if self.mode == AES.MODE_ECB :
      cipher = AES.new(self.key, self.mode)
    else :
      cipher = AES.new(self.key, self.mode, self.initial_vector)
    return lambda plain_text : base64.b64encode(cipher.encrypt(self.pad(plain_text.encode("utf8")))) 
    
  def encrypt(self, plain_text) :
    encrypted_text = self.encryptor(plain_text)
    return encrypted_text.decode("utf8")
