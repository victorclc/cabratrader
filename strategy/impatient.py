from core.strategy import CycleStrategy, CycleState
from database.datamanager import DataManager
from exchange.models import TradeStream


class Impatient(CycleStrategy):
    def on_trade_update(self, trade: TradeStream):
        if self.cycle.state == CycleState.COMPLETED:
            return
        elif self.cycle.state == CycleState.WATCHING or self.cycle.state == CycleState.BUYING:
            analysis = self.setup.analysis.trade.watching.analyze(trade, 0.0, self.setup.target, self.setup.max_loss)
        else:
            analysis = self.setup.analysis.trade.holding.analyze(trade, self.cycle.avg_buy_price, self.setup.target,
                                                                 self.setup.max_loss)

        if self.cycle.state == CycleState.BOUGHT:
            self.take_action(analysis)

        if analysis.order_id:
            analysis.symbol = self.symbol
            DataManager.persist(analysis)

    def on_chart_update(self, chart):
        if self.cycle.state == CycleState.WATCHING or self.cycle.state == CycleState.BUYING:
            analysis = self.setup.analysis.chart.watching.analyze(chart)
        else:
            analysis = self.setup.analysis.chart.holding.analyze(chart)
            if analysis.suggestion != 'SELL':
                time_analysis = self.setup.analysis.time.holding.analyze(self.cycle, chart)
                if time_analysis.suggestion:
                    analysis = time_analysis
                    self.lock_buy = True

        self.take_action(analysis)

        analysis.symbol = self.symbol
        DataManager.persist(analysis)

        if self.cycle.state == CycleState.COMPLETED:
            self.handle_cycle_completed()
