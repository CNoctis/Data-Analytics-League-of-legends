class UserData(object):
    """
    It will provide the necessary information for the operation of the program.
    """
    def __init__(self, token:str, user:str, region:str, date_ini:str):
        """
        token: Token provided by the riot api (str)
        user: Username (str)
        region: player region (BR, NA, LAN, LAS, KR, JP, EUN, EUW, TR, RU, OCE)
        date_ini: Search start date (Y/m/d)
        """
        #Token verification
        if len(token) > 0:
            self.token = token
        else:
            raise TypeError ("token string cannot be empty")
        
        #Username Verification
        if len(user) > 0:
            self.user = user
        else:
            raise TypeError ("Username cannot be an empty string")
        
        #Region verification
        if len(region) > 0:
            self.region = region
        else:
            raise TypeError ("Region cannot be an empty string")
        
        #Date Verification
        if len(date_ini) >0:
            self.date_ini= date_ini
        else:
            raise TypeError ("Date cannot be an empty string")
    

    def __str__(self):
        return f'Token:{self.token}, User:{self.user}, Region:{self.region}, Fecha de inicio:{self.date_ini}'