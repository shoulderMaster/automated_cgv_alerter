from Crypto.Cipher import AES
import base64

correct_input = "20190514"
correct_output = "uU8HUn3rxCYRKgs3pGahCA=="
cgv_aes_key = bytes([ 86, 66, 65, 49, 78, 85, 83, 54, 84, 56, 85, 73, 68, 50, 73, 54, 79, 66, 70, 55, 49, 53, 56, 56, 57, 57, 67, 84, 52, 70, 51, 67 ])
cgv_aes_IV = bytes([ 86, 66, 65, 49, 78, 85, 83, 54, 84, 56, 85, 73, 68, 50, 73, 54 ])

class cgv_crypto :
  def __init__(self, key, IV, mode) :
    self.BLOCK_SIZE = 16
    self.encryption_mode = mode
    self.mode = mode
    self.key = key
    self.initial_vector = IV
    self.encryptor = self.make_encryptor()

  #PKCS7 padding algorithm
  def pad(self, data) :
    padding = bytes([(16-len(data))%16])
    padded_data = (data+padding*16)[:16]
    return padded_data

  def make_encryptor(self) :
    if self.mode == AES.MODE_ECB :
      cipher = AES.new(self.key, self.mode)
    else :
      cipher = AES.new(self.key, self.mode, self.initial_vector)
    return lambda plain_text : base64.b64encode(cipher.encrypt(self.pad(plain_text.encode("utf8")))) 
    
  def encrypt(self, plain_text) :
    encrypted_text = self.encryptor(plain_text)
    return encrypted_text

def main() :
  crypto = cgv_crypto(key=cgv_aes_key, IV=cgv_aes_IV, mode=AES.MODE_CBC)
  enc_txt = crypto.encrypt(correct_input)
  print("encrypted text : %s" % enc_txt)
  print("correct output : %s" % correct_output)
  print("input : %s" % correct_input)

main()
