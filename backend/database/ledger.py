import hashlib
import json
from datetime import datetime
from backend.database.models import db, BlockchainLedger
import logging

logger = logging.getLogger(__name__)

class LedgerService:
    
    @staticmethod
    def calculate_merkle_root(transactions):
        if not transactions:
            return hashlib.sha256(b'').hexdigest()
        
        hashes = [
            hashlib.sha256(json.dumps(t, sort_keys=True).encode()).hexdigest()
            for t in transactions
        ]
        
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])
            
            hashes = [
                hashlib.sha256((hashes[i] + hashes[i+1]).encode()).hexdigest()
                for i in range(0, len(hashes), 2)
            ]
        
        return hashes[0]
    
    @staticmethod
    def add_transaction(transaction_type, transaction_id, **kwargs):
        try:
            # Get previous block
            previous_block = BlockchainLedger.query.order_by(
                BlockchainLedger.block_number.desc()
            ).first()
            
            previous_hash = previous_block.block_hash if previous_block else '0' * 64
            block_number = (previous_block.block_number + 1) if previous_block else 1
            
            # Create transaction data
            transaction_data = {
                'type': transaction_type,
                'id': transaction_id,
                **kwargs
            }
            
            # Calculate merkle root
            merkle_root = LedgerService.calculate_merkle_root([transaction_data])
            
            # Mine block
            nonce = 0
            timestamp = datetime.utcnow()
            
            while True:
                block_content = f"{block_number}{timestamp.isoformat()}{transaction_type}{transaction_id}{previous_hash}{merkle_root}{nonce}"
                block_hash = hashlib.sha256(block_content.encode()).hexdigest()
                
                if block_hash.startswith('0'):
                    break
                nonce += 1
                
                if nonce > 1000000:
                    logger.warning("Mining difficulty too high, accepting current hash")
                    break
            
            # Create ledger entry
            ledger_entry = BlockchainLedger(
                block_number=block_number,
                timestamp=timestamp,
                transaction_type=transaction_type,
                transaction_id=transaction_id,
                portfolio_id=kwargs.get('portfolio_id'),
                seller_id=kwargs.get('seller_id'),
                buyer_id=kwargs.get('buyer_id'),
                amount=kwargs.get('amount'),
                previous_hash=previous_hash,
                block_hash=block_hash,
                merkle_root=merkle_root,
                nonce=nonce
            )
            
            db.session.add(ledger_entry)
            db.session.commit()
            
            logger.info(f"Block {block_number} added to ledger: {transaction_type}")
            
            return {
                'block_number': block_number,
                'block_hash': block_hash,
                'transaction_id': transaction_id,
                'timestamp': timestamp.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding transaction to ledger: {str(e)}")
            raise
    
    @staticmethod
    def validate_chain():
        try:
            blocks = BlockchainLedger.query.order_by(BlockchainLedger.block_number).all()
            
            if not blocks:
                return True, "Chain is empty"
            
            for i in range(1, len(blocks)):
                current_block = blocks[i]
                previous_block = blocks[i-1]
                
                # Verify previous hash linkage
                if current_block.previous_hash != previous_block.block_hash:
                    return False, f"Block {current_block.block_number} has invalid previous_hash"
                
                # Verify block hash
                block_content = f"{current_block.block_number}{current_block.timestamp.isoformat()}{current_block.transaction_type}{current_block.transaction_id}{current_block.previous_hash}{current_block.merkle_root}{current_block.nonce}"
                calculated_hash = hashlib.sha256(block_content.encode()).hexdigest()
                
                if calculated_hash != current_block.block_hash:
                    return False, f"Block {current_block.block_number} has invalid hash"
            
            return True, "Chain is valid"
            
        except Exception as e:
            logger.error(f"Error validating chain: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def query_ledger(filters=None):
        try:
            query = BlockchainLedger.query
            
            if filters:
                if 'transaction_type' in filters:
                    query = query.filter(BlockchainLedger.transaction_type == filters['transaction_type'])
                if 'portfolio_id' in filters:
                    query = query.filter(BlockchainLedger.portfolio_id == filters['portfolio_id'])
            
            return query.order_by(BlockchainLedger.block_number.desc()).all()
            
        except Exception as e:
            logger.error(f"Error querying ledger: {str(e)}")
            return []
