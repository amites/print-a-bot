from logging import getLogger

logger = getLogger('Print-a-bot')


def light(led, R, B, C):
    logger.info('light was called with: led:{}'.format(led))
    logger.info('red was called with: R:{}' .format(R))
    logger.info('blue was called with: B:{}' .format(B))
    logger.info('green was called with: G:{}'.format(C))
    return True


def motor(motor, speed):
    logger.info('motor was called with: motor : {}'.format(motor))
    logger.info('speed was called with: speed : {}'.format(speed))
    return True
