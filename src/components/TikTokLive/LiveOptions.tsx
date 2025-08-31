import { useState } from 'react';
import coinIcon from '../../assets/coin.png';
import OptionDonateModal from './OptionDonateModal.js';

interface Option {
  id: number;
  desc: string;
  moneyGoal: number;
  moneyCurrent: number;
}

const LiveOptions = ({displayed}: {displayed: boolean}) => {
  const [options, setOptions] = useState<Option[]>([
    { id: 1, desc: "Finish a croissant in 30s", moneyGoal: 10, moneyCurrent: 9},
    { id: 2, desc: "Treat a stranger a free drink", moneyGoal: 5, moneyCurrent: 5},
    { id: 3, desc: "Pastry Mukbang Challenge", moneyGoal: 30, moneyCurrent: 14},
  ]);

  const [openedOption, setOpenedOption] = useState<Option>();

  const [isOpen, setIsOpen] = useState<boolean>(false);

  const handleToggleModal = (op: Option) => {
    setOpenedOption(op);
    setIsOpen(!isOpen);
  }

  return (
    <>
      {openedOption && <OptionDonateModal option={openedOption} displayed={isOpen} setDisplayed={handleToggleModal}/>}
      <view className="options-container" style={displayed ? 'display: block' : 'display: none'}>
        {/* Comments List */}
        <view className="chat-list">
          {options.map((op) => (
            <view key={op.id} className={`option-bubble ${op.moneyCurrent >= op.moneyGoal ? "money-achieved" : ""}`} style="position: relative;">
              <text className="chat-description">
                {op.desc}
              </text>
              <view className="rightside-container">
                <view className="chat-money-container">
                  {op.moneyCurrent >= op.moneyGoal ? <></> : <text className="curr-amt">${op.moneyCurrent}</text>}
                  {op.moneyCurrent >= op.moneyGoal ? <></> : <text className="money-delimiter">of</text>}
                  {op.moneyCurrent >= op.moneyGoal ? <text className="goal-amt-not-reached">${op.moneyGoal}</text> : <text className="goal-amt">${op.moneyGoal}</text>}
                </view>
                {op.moneyCurrent >= op.moneyGoal ? <></> : 
                  <view className="pool-cash-btn" bindtap={() => handleToggleModal(op)}>
                    <image src={coinIcon} className="coin"/>
                  </view>}
              </view>
            </view>
          ))}
        </view>
      </view>
    </>
  );
};

export default LiveOptions;