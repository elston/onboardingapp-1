class BaseService:
    def __init__(self):
        pass

    def getParameterForm():
        raise NotImplementedError("Service Implementaion must override")

    def processParameterForm():
        raise NotImplementedError("Service Implementaion must override")

    def getMemeberList():
        raise NotImplementedError("Service Implementaion must override")

    def addMemberByEmail():
        raise NotImplementedError("Service Implementaion must override")

    def removeMember(member):
        raise NotImplementedError("Service Implementaion must override")
