from collections import OrderedDict

from . import BlockHeader, BlockBody
from .. import Block, BlockSerializer as BaseBlockSerializer
from ... import Hash32, ExternalAddress, Signature, BloomFilter, TransactionSerializer


class BlockSerializer(BaseBlockSerializer):
    version = BlockHeader.version
    BlockHeaderClass = BlockHeader
    BlockBodyClass = BlockBody

    def _serialize(self, block: 'Block'):
        header: BlockHeader = block.header
        body: BlockBody = block.body

        transactions = list()
        for tx in body.transactions.values():
            ts = TransactionSerializer.new(tx.version, self._tx_versioner)
            tx_serialized = ts.to_full_data(tx)
            transactions.append(tx_serialized)

        return {
            "version": header.version,
            "prev_block_hash": header.prev_hash.hex() if header.prev_hash else '',
            "merkle_tree_root_hash": header.transaction_root_hash.hex() if header.transaction_root_hash else '',
            "state_root_hash": header.state_root_hash.hex() if header.state_root_hash else '',
            "receipt_root_hash": header.receipt_root_hash.hex() if header.receipt_root_hash else '',
            "rep_root_hash": header.rep_root_hash.hex(),
            "bloom_filter": header.bloom_filter.hex(),
            "time_stamp": header.timestamp,
            "confirmed_transaction_list": transactions,
            "block_hash": header.hash.hex(),
            "height": header.height,
            "peer_id": header.peer_id.hex_hx() if header.peer_id else '',
            "signature": header.signature.to_base64str() if header.signature else '',
            "next_leader": header.next_leader.hex_xx(),
            "complained": 1 if header.complained else 0,
        }

    def _deserialize_header_data(self, json_data: dict):
        prev_hash = json_data.get('prev_block_hash')
        prev_hash = Hash32.fromhex(prev_hash, ignore_prefix=True) if prev_hash else None

        peer_id = json_data.get('peer_id')
        peer_id = ExternalAddress.fromhex(peer_id) if peer_id else None

        signature = json_data.get('signature')
        signature = Signature.from_base64str(signature) if signature else None

        next_leader = json_data.get("next_leader")
        next_leader = ExternalAddress.fromhex(next_leader) if next_leader else None

        tx_root_hash = json_data["merkle_tree_root_hash"]
        tx_root_hash = Hash32.fromhex(tx_root_hash, ignore_prefix=True) if tx_root_hash else None

        receipt_root_hash = json_data["receipt_root_hash"]
        receipt_root_hash = Hash32.fromhex(receipt_root_hash, ignore_prefix=True) if receipt_root_hash else None

        state_root_hash = json_data["state_root_hash"]
        state_root_hash = Hash32.fromhex(state_root_hash, ignore_prefix=True) if state_root_hash else None

        rep_root_hash = json_data["rep_root_hash"]
        rep_root_hash = Hash32.fromhex(rep_root_hash, ignore_prefix=True) if state_root_hash else None

        if json_data["complained"] == 1:
            complained = True
        elif json_data["complained"] == 0:
            complained = False
        else:
            raise RuntimeError

        return {
            "hash": Hash32.fromhex(json_data["block_hash"], ignore_prefix=True),
            "prev_hash": prev_hash,
            "height": json_data["height"],
            "timestamp": json_data["time_stamp"],
            "peer_id": peer_id,
            "signature": signature,
            "next_leader": next_leader,
            "transaction_root_hash": tx_root_hash,
            "receipt_root_hash": receipt_root_hash,
            "state_root_hash": state_root_hash,
            "rep_root_hash": rep_root_hash,
            "bloom_filter": BloomFilter.fromhex(json_data["bloom_filter"], ignore_prefix=True),
            "complained": complained
        }

    def _deserialize_body_data(self, json_data: dict):
        confirm_prev_block = json_data.get("confirm_prev_block")

        transactions = OrderedDict()
        for tx_data in json_data['confirmed_transaction_list']:
            tx_version = self._tx_versioner.get_version(tx_data)
            ts = TransactionSerializer.new(tx_version, self._tx_versioner)
            tx = ts.from_(tx_data)
            transactions[tx.hash] = tx

        return {
            "transactions": transactions,
            "confirm_prev_block": confirm_prev_block
        }
