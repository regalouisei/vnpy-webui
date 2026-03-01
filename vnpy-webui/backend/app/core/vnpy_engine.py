# VnPy 引擎封装

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.ctp.gateway import CtpGateway
from vnpy_ctastrategy import CtaEngine

from app.utils.config import settings

class VnPyEngine:
    """VnPy 引擎封装类"""
    
    def __init__(self):
        self.event_engine = EventEngine()
        self.main_engine = MainEngine(self.event_engine)
        self.cta_engine = None
        self.connected = False
    
    def connect(self, gateway_setting: dict, gateway_name: str = "CTP"):
        """连接网关"""
        try:
            self.main_engine.add_gateway(CtpGateway, gateway_name)
            self.main_engine.connect(gateway_setting, gateway_name)
            self.connected = True
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def add_cta_engine(self):
        """添加 CTA 策略引擎"""
        try:
            self.cta_engine = self.main_engine.add_engine(CtaEngine)
            self.cta_engine.init_engine()
            return True
        except Exception as e:
            print(f"添加 CTA 引擎失败: {e}")
            return False
    
    def get_account(self):
        """获取账户信息"""
        oms_engine = self.main_engine.get_engine("oms")
        accounts = oms_engine.get_all_accounts()
        if accounts:
            return accounts[0]
        return None
    
    def get_position(self, symbol: str):
        """获取持仓信息"""
        oms_engine = self.main_engine.get_engine("oms")
        positions = oms_engine.get_all_positions()
        for pos in positions:
            if pos.symbol == symbol:
                return pos
        return None
    
    def get_all_positions(self):
        """获取所有持仓"""
        oms_engine = self.main_engine.get_engine("oms")
        return oms_engine.get_all_positions()
    
    def get_all_contracts(self):
        """获取所有合约"""
        oms_engine = self.main_engine.get_engine("oms")
        return oms_engine.get_all_contracts()
    
    def subscribe(self, symbol: str, exchange):
        """订阅行情"""
        from vnpy.trader.object import SubscribeRequest
        
        req = SubscribeRequest(
            symbol=symbol,
            exchange=exchange
        )
        self.main_engine.subscribe(req, "CTP")
    
    def close(self):
        """关闭连接"""
        # TODO: 实现关闭逻辑
        pass
