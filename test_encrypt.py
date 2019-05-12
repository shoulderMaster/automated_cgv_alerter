from Crypto.Cipher import AES
import base64

correct_input = "20190514"
correct_output = "uU8HUn3rxCYRKgs3pGahCA=="

class cgv_crypto :
  def __init__(self) :
    self.BLOCK_SIZE = 16
    self.padding_list = ["0", "\0", " "]

  def get_padded_list(self, key_component) :
    key_list = [(key_component+pad*16)[:self.BLOCK_SIZE] for pad in self.padding_list]
    key_list.append((key_component*16)[:16])
    return key_list

  def make_encryptor(self, key) :
    cipher = AES.new(key)
    #return lambda plain_text : base64.b64encode(cipher.encrypt(plain_text.encode("utf8"))) 
    return lambda plain_text : base64.b64encode(cipher.encrypt(plain_text)) 
    
  def encrypt(self, plain_text) :
    plain_text = plain_text.encode("utf8")
    #padded_plain_list = self.get_padded_list(plain_text)
    #key_list = padded_plain_list
    key_list = [plain_text]
    padded_plain_list = [plain_text]
    encryptor_list = [self.make_encryptor(key) for key in key_list]
    encrypted_list = [enc(padded_plain_list[idx]) for idx, enc in enumerate(encryptor_list)]
    print(encrypted_list)
    return encrypted_list

def main() :
  crypto = cgv_crypto()
  crypto.encrypt(correct_input)
  print("correct output : %s" % correct_output)
  print("input : %s" % correct_input)

main()
