import heapq
import logging as log
import time
import brokerutils

log = brokerutils.setup_logging(__name__)


class BADLSCCache:
    class CachedObject:
        def __init__(self, key=None, channelSubscriptionId=None, channelExecutionTime=None, userIds=[], timestamp=None, object=None):
            self.key = key
            self.channelSubscriptionId = channelExecutionTime
            self.channelExecutionTime = channelExecutionTime
            self.userIds = userIds
            self.timestamp = timestamp
            self.object = object

        def __repr__(self):
            return self.key

        def __str__(self):
            return str(self.key)

        def __cmp__(self, other):
            return len(self.userIds) - len(other.userIds)

        def __lt__(self, other):
            if len(self.userIds) == len(other.userIds):
                return self.timestamp < other.timestamp

            return len(self.userIds) < len(other.userIds)

        def __eq__(self, other):
            return self.key == other.key

        def __hash__(self):
            return self.key.__hash__()


    def __init__(self, size=100):
        self.cache = {}
        self.cachedObjects = []
        self.size = size
        self.leastSubscribedObject = None

    def get(self, key, **kwargs):
        log.info('Getting item with key {}'.format(key))
        cachedObject = None
        if kwargs:
            channelSubscriptionId = kwargs['channelSubscriptionId']
            channelExecutionTime = kwargs['channelExecutionTime']
            userId = kwargs['userId']

            try:
                cachedObject = self.cache[channelSubscriptionId][channelExecutionTime]

                if userId in cachedObject.userIds:
                    cachedObject.userIds.remove(userId)

                cachedObject.timestamp = time.time()

                if self.leastSubscribedObject is None or cachedObject < self.leastSubscribedObject:
                    self.leastSubscribedObject = cachedObject

            except KeyError as e:
                pass

        if cachedObject:
            log.info('Object found {}'.format(cachedObject))
            cachedObject.object
        else:
            log.warning('Object not found in the cache with key {}'.format(key))
            return None

    def put(self, key, object, **kwargs):
        log.info('Putting new item into the cache with key {}'.format(key))
        if kwargs:
            channelSubscriptionId = kwargs['channelSubscriptionId']
            channelExecutionTime = kwargs['channelExecutionTime']
            userIds = kwargs['userIds']

            cachedObject = BADLSCCache.CachedObject()
            cachedObject.key = key
            cachedObject.object = object
            cachedObject.channelSubscriptionId = channelSubscriptionId
            cachedObject.channelExecutionTime = channelExecutionTime
            cachedObject.userIds = userIds
            cachedObject.timestamp = time.time()

            if channelSubscriptionId not in self.cache:
                self.cache[channelSubscriptionId]= {}

            self.cache[channelSubscriptionId][channelExecutionTime] = cachedObject

            self.cachedObjects.append(cachedObject)

            if self.leastSubscribedObject is None or cachedObject < self.leastSubscribedObject:
                    self.leastSubscribedObject = cachedObject

            # Eviction
            if len(self.cachedObjects) > self.size:
                if self.leastSubscribedObject is None:
                    self.leastSubscribedObject = min(self.cachedObjects)

                log.info('Deleting item {} with subscription count {}'.format(self.leastSubscribedObject, len(self.leastSubscribedObject.userIds)))

                self.cachedObjects.remove(self.leastSubscribedObject)
                del self.cache[self.leastSubscribedObject.channelSubscriptionId][self.leastSubscribedObject.channelExecutionTime]

                self.leastSubscribedObject = min(self.cachedObjects) if len(self.cachedObjects) > 0 else None


if __name__ == '__main__':
    cache = BADLSCCache(3)

    cache.put(101, "ABC", channelSubscriptionId=1, channelExecutionTime=1, userIds=[1, 3])
    cache.put(102, "ABC", channelSubscriptionId=1, channelExecutionTime=2, userIds=[2, 4])
    cache.put(103, "ABC", channelSubscriptionId=1, channelExecutionTime=3, userIds=[1, 3])

    cache.get(102, channelSubscriptionId=1, channelExecutionTime=2, userId=2)
    cache.get(102, channelSubscriptionId=1, channelExecutionTime=2, userId=4)

    cache.put(104, "ABC", channelSubscriptionId=1, channelExecutionTime=4, userIds=[1, 2, 3, 4])
